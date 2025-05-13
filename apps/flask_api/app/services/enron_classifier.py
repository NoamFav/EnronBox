from app.services.emotion_enhancer import EmotionEnhancer
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.db import store_data
import sqlite3

import pandas as pd
import numpy as np
import re
import os, pickle
import email
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

# Rich for beautiful console output
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from typing import Dict, Any
from rich.table import Table
from rich import box
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path

logging.getLogger("nltk").setLevel(logging.ERROR)

try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords", quiet=True)


class EnronEmailClassifier:
    def __init__(self, model_dir="models"):

        text_path = Path(model_dir) / "text_model.pkl"
        num_path = Path(model_dir) / "num_model.pkl"

        if text_path.exists() and num_path.exists():
            # load existing models
            with open(text_path, "rb") as f:
                self.text_model = pickle.load(f)
            with open(num_path, "rb") as f:
                self.numerical_model = pickle.load(f)
        else:
            # not trained yet
            self.text_model = None
            self.numerical_model = None
        # Initialize Rich Console
        self.console = Console()

        self.categories = [
            "Work",
            "Urgent",
            "Business",
            "Personal",
            "Meeting",
            "External",
            "Newsletter",
        ]
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.emotion_enhancer = EmotionEnhancer()
        self.label_map = None
        self.stop_words = set(stopwords.words("english"))

    def _rich_print(self, message, style="bold green"):
        """Print message with Rich formatting"""
        self.console.print(
            Panel(
                Text(message, style=style),
                border_style=style.split()[1] if len(style.split()) > 1 else style,
            )
        )

    def preprocess_text(self, text):
        """Clean and preprocess the email text"""
        if isinstance(text, float) and np.isnan(text):
            return ""

        # Convert to string if it's not already
        text = str(text)

        # Convert to lowercase
        text = text.lower()

        # Remove HTML tags
        text = re.sub(r"<.*?>", "", text)

        # Remove special characters and numbers
        text = re.sub(r"[^a-zA-Z\s]", "", text)

        # Tokenize text
        tokens = text.split()

        # Remove stopwords and lemmatize
        cleaned_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]

        return " ".join(cleaned_tokens)

    def load_enron_emails(self, enron_db_path: str, max_emails: int = 5000):
        """
        Load up to `max_emails` from the SQLite DB at `enron_db_path`,
        map each folder → a category index, and return (df, labels).
        """
        # 1) grab the raw table of emails + folder names
        conn = sqlite3.connect(enron_db_path)
        query = """
            SELECT
                e.id AS email_id,
                e.from_address    AS sender,
                e.subject         AS subject,
                e.body            AS body,
                f.name            AS folder_name,
                e.date            AS time_sent
            FROM emails e
            JOIN folders f ON e.folder_id = f.id
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(max_emails,))
        conn.close()

        # 2) fill in any numerical cols your train() expects
        df["has_attachment"] = False
        df["num_recipients"] = 1
        # convert time_sent to actual datetime:
        df["time_sent"] = pd.to_datetime(df["time_sent"], errors="coerce")

        # 3) map folder_name → a numeric label index
        labels = []
        for folder in df["folder_name"]:
            idx = next(
                (
                    i
                    for i, cat in enumerate(self.categories)
                    if cat.lower() in folder.lower()
                ),
                None,
            )
            if idx is None:
                # fallback logic copied from your maildir loader
                lname = folder.lower()
                if "sent" in lname:
                    idx = self.categories.index("Business")
                elif "inbox" in lname:
                    idx = self.categories.index("Personal")
                elif "deleted" in lname:
                    idx = self.categories.index("External")
                else:
                    idx = self.categories.index("Work")
            labels.append(idx)

        # 4) drop helper columns
        df = df.drop(columns=["folder_name"])

        # 5) return the DataFrame & a numpy array of label‐indices
        return df, np.array(labels, dtype=int)

    def _process_folder(
        self,
        folder_path,
        category_idx,
        emails,
        labels,
        max_emails,
        progress=None,
        task_id=None,
        overall_task=None,
        processed_count=None,
        username=None,
    ):
        """Process all emails in a folder and its subfolders"""
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isdir(file_path):
                self._process_folder(
                    file_path,
                    category_idx,
                    emails,
                    labels,
                    max_emails,
                    progress,
                    task_id,
                    overall_task,
                    processed_count,
                    username,
                )
                continue

            if len(emails) >= max_emails:
                return

            try:
                with open(file_path, "r", encoding="latin1", errors="ignore") as f:
                    msg_content = f.read()
                msg = email.message_from_string(msg_content)
                subject = msg.get("Subject", "")
                sender = msg.get("From", "")
                date_str = msg.get("Date", "")
                cc = msg.get("Cc", "")
                num_recipients = 1
                if cc:
                    num_recipients += cc.count("@")
                try:
                    time_sent = pd.to_datetime(date_str)
                except ValueError:
                    time_sent = pd.Timestamp("2000-01-01")
                body = self._extract_email_body(msg)
                has_attachment = False
                for part in msg.walk():
                    if part.get_content_maintype() != "multipart" and part.get(
                        "Content-Disposition"
                    ):
                        has_attachment = True
                        break

                emails.append(
                    {
                        "subject": subject,
                        "body": body,
                        "sender": sender,
                        "has_attachment": has_attachment,
                        "num_recipients": num_recipients,
                        "time_sent": time_sent,
                    }
                )
                labels.append(category_idx)

                # Update user task progress
                if progress and task_id:
                    progress.update(task_id, advance=1)
                # Update the overall progress using the shared counter
                if processed_count is not None and overall_task is not None:
                    processed_count[0] += 1
                    assert progress is not None
                    progress.update(overall_task, completed=processed_count[0])

            except FileNotFoundError as e:
                print(f"File not found: {file_path}. Error: {e}")
            except ValueError as e:
                print(f"Invalid value encountered in {file_path}. Error: {e}")
            except TypeError as e:
                print(f"Type error in processing {file_path}. Error: {e}")
            except AttributeError as e:
                print(f"Missing attribute in email from {file_path}. Error: {e}")

    def _extract_email_body(self, msg):
        """Extract the body text from an email message"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        if isinstance(payload, bytes):
                            body += payload.decode("latin1", errors="ignore")
                        else:
                            body += str(payload)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                if isinstance(payload, bytes):
                    body = payload.decode("latin1", errors="ignore")
                else:
                    body = str(payload)

        return body

    def extract_features(self, email_data):
        """Extract features from emails including enhanced emotion metrics"""
        features = pd.DataFrame()

        # Check if required columns exist
        required_columns = [
            "body",
            "subject",
            "sender",
            "has_attachment",
            "num_recipients",
            "time_sent",
        ]
        missing_columns = [
            col for col in required_columns if col not in email_data.columns
        ]

        default_values = {
            "body": "",
            "subject": "",
            "sender": "",
            "has_attachment": False,
            "num_recipients": 1,
            "time_sent": pd.Timestamp("2000-01-01"),
        }

        if missing_columns:
            print(f"Warning: Missing columns in email_data: {missing_columns}")
            for col in missing_columns:
                # Set the column to its default value
                if col in default_values:
                    email_data[col] = default_values[col]

        # Preprocess email body
        features["cleaned_text"] = email_data["body"].apply(self.preprocess_text)

        # Apply the EmotionEnhancer to each email body
        emotion_results = email_data["body"].apply(
            self.emotion_enhancer.enhance_emotion_analysis
        )

        # Extract emotion metrics directly into separate columns
        features["polarity"] = emotion_results.apply(lambda x: x["polarity"])
        features["subjectivity"] = emotion_results.apply(lambda x: x["subjectivity"])
        features["stress_score"] = emotion_results.apply(lambda x: x["stress_score"])
        features["relaxation_score"] = emotion_results.apply(
            lambda x: x["relaxation_score"]
        )

        # Extract email metadata features
        features["subject_length"] = email_data["subject"].apply(
            lambda x: len(str(x)) if not pd.isna(x) else 0
        )
        features["body_length"] = email_data["body"].apply(
            lambda x: len(str(x)) if not pd.isna(x) else 0
        )
        features["has_attachment"] = email_data["has_attachment"].astype(
            int
        )  # Convert boolean to int
        features["num_recipients"] = email_data["num_recipients"]

        # Extract hour from time_sent
        features["time_sent_hour"] = email_data["time_sent"].apply(
            lambda x: x.hour if not pd.isna(x) else 12
        )

        # Check for urgency keywords in subject
        urgent_keywords = ["urgent", "asap", "immediately", "deadline", "important"]
        features["urgent_subject"] = (
            email_data["subject"]
            .apply(
                lambda x: (
                    any(keyword in str(x).lower() for keyword in urgent_keywords)
                    if not pd.isna(x)
                    else False
                )
            )
            .astype(int)
        )  # Convert boolean to int

        # Check for excessive punctuation
        features["exclamation_count"] = email_data["subject"].apply(
            lambda x: str(x).count("!") if not pd.isna(x) else 0
        )

        # Check for common business phrases
        business_phrases = [
            "meeting",
            "report",
            "project",
            "update",
            "budget",
            "client",
        ]
        features["business_score"] = email_data["body"].apply(
            lambda x: (
                sum(1 for phrase in business_phrases if phrase in str(x).lower())
                if not pd.isna(x)
                else 0
            )
        )

        # Check for external vs internal emails
        features["is_external"] = (
            email_data["sender"]
            .apply(
                lambda x: "enron.com" not in str(x).lower() if not pd.isna(x) else True
            )
            .astype(int)
        )

        return features

    def display_classification_report(self, actual_categories, predicted_categories):
        report = classification_report(
            actual_categories, predicted_categories, output_dict=True
        )

        table = Table(
            title="🎯 Classification Report",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold white on dark_blue",
            title_style="bold green",
            expand=False,
        )

        table.add_column("Label", style="cyan", no_wrap=True)
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("F1-Score", justify="right")
        table.add_column("Support", justify="right")

        for label, metrics in report.items():
            if isinstance(metrics, dict):
                table.add_row(
                    str(label),
                    f"{metrics['precision']:.2f}",
                    f"{metrics['recall']:.2f}",
                    f"{metrics['f1-score']:.2f}",
                    str(int(metrics["support"])),
                )
            elif label == "accuracy":
                table.add_row(
                    "accuracy",
                    "",
                    "",
                    f"{metrics:.2f}",
                    str(int(report["macro avg"]["support"])),
                )

        self.console.print(table)

    def train(self, email_data, labels):
        """Train the email classifier model with Rich progress and visualization"""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=True,
            console=self.console,
        ) as progress:
            # Define a training task with 6 steps (you can adjust total if you add more)
            train_task = progress.add_task(
                "[bold green]Training Email Classifier...", total=6
            )

            # Extract Features
            progress.update(
                train_task, description="[bold green]Extracting Features..."
            )
            features = self.extract_features(email_data)
            progress.advance(train_task)

            # Prepare Labels
            progress.update(train_task, description="[bold green]Preparing Labels...")
            unique_labels = np.unique(labels)
            n_classes = len(unique_labels)
            train_label_map = {label: i for i, label in enumerate(unique_labels)}
            mapped_labels = np.array([train_label_map[label] for label in labels])
            progress.advance(train_task)

            # Update Categories
            progress.update(
                train_task, description="[bold green]Updating Categories..."
            )
            self.categories = [
                (
                    self.categories[label]
                    if label < len(self.categories)
                    else f"Class_{label}"
                )
                for label in unique_labels
            ]
            progress.advance(train_task)

            # Split Dataset
            progress.update(train_task, description="[bold green]Splitting Dataset...")
            X_train, X_test, y_train, y_test = train_test_split(
                features, mapped_labels, test_size=0.2, random_state=42
            )
            progress.advance(train_task)

            # Train Models (Text and Numerical)
            progress.update(
                train_task,
                description="[bold green]Training Models (Text & Numerical)...",
            )
            # Train text model
            text_pipeline = Pipeline(
                [
                    ("tfidf", TfidfVectorizer(max_features=5000)),
                    (
                        "classifier",
                        RandomForestClassifier(n_estimators=100, random_state=42),
                    ),
                ]
            )
            train_text = X_train["cleaned_text"].values
            test_text = X_test["cleaned_text"].values
            text_pipeline.fit(train_text, y_train)

            # Train numerical model
            numerical_features = X_train.drop(columns=["cleaned_text"])
            numerical_classifier = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            numerical_classifier.fit(numerical_features, y_train)

            # Store models
            self.text_model = text_pipeline
            self.numerical_model = numerical_classifier
            self.label_map = train_label_map
            progress.advance(train_task)

            # Evaluate Models
            progress.update(train_task, description="[bold green]Evaluating Models...")
            text_proba = text_pipeline.predict_proba(test_text)
            numerical_proba = numerical_classifier.predict_proba(
                X_test.drop(columns=["cleaned_text"])
            )
            combined_proba = (text_proba + numerical_proba) / 2
            combined_predictions = np.argmax(combined_proba, axis=1)
            predicted_categories = [self.categories[i] for i in combined_predictions]
            actual_categories = [self.categories[i] for i in y_test]
            progress.advance(train_task)

        # After training, show a detailed results table
        results_table = Table(
            title="🚀 Model Training Results",
            title_style="bold green",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold white on dark_blue",
            expand=False,
            pad_edge=False,
        )

        results_table.add_column(
            "📊 Metric", style="cyan", justify="left", no_wrap=True
        )
        results_table.add_column("📈 Value", style="magenta", justify="left")

        results_table.add_row("Classes", ", ".join(self.categories))
        results_table.add_row("Number of Classes", str(n_classes))

        self.console.print(results_table)

        # Print the classification report
        self.display_classification_report(actual_categories, predicted_categories)

        base_dir = Path(__file__).resolve().parent.parent
        results_dir = base_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Save additional visualizations if more than one class exists
        if len(np.unique(actual_categories)) > 1:
            plt.figure(figsize=(10, 8))
            cm = confusion_matrix(
                actual_categories, predicted_categories, labels=self.categories
            )
            sns.heatmap(
                cm,
                annot=True,
                fmt="d",
                cmap="Blues",
                xticklabels=self.categories,
                yticklabels=self.categories,
            )
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.title("Confusion Matrix")
            plt.tight_layout()
            conf_matrix_path = results_dir / "confusion_matrix.png"
            plt.savefig(conf_matrix_path)

            # Save Feature Importance Plot
            feature_importances = self.numerical_model.feature_importances_
            feature_names = X_train.drop(columns=["cleaned_text"]).columns

            # Sort features by importance
            importance_df = pd.DataFrame(
                {"feature": feature_names, "importance": feature_importances}
            ).sort_values(
                by="importance", ascending=False
            )  # Ascending for horizontal bar plot

            plt.figure(figsize=(12, 8))
            sns.barplot(x="feature", y="importance", data=importance_df)
            plt.title("Feature Importances")
            plt.xlabel("Importance")
            plt.ylabel("Feature")
            plt.tight_layout()

            feat_imp_path = results_dir / "feature_importance.png"
            plt.savefig(feat_imp_path)

        return self

    def predict(self, message):
        """Predict the category of a new email"""
        if self.text_model is None or self.numerical_model is None:
            raise ValueError(
                "Model not trained yet."
                "Please train both the text and numerical models before use."
            )
        # Convert single email to DataFrame format
        if isinstance(message, dict):
            email_df = pd.DataFrame([message])
        else:
            email_df = message

        # Extract features
        features = self.extract_features(email_df)

        # Get predictions from both models
        text_proba = self.text_model.predict_proba([features["cleaned_text"].iloc[0]])[
            0
        ]

        # Make sure to only include numerical features (exclude the text column)
        numerical_features = features.drop(columns=["cleaned_text"])
        numerical_proba = self.numerical_model.predict_proba(
            numerical_features.iloc[0:1]
        )[0]

        # Combine predictions
        combined_proba = (text_proba + numerical_proba) / 2
        predicted_class = np.argmax(combined_proba)

        # Return category, confidence, and emotion analysis
        return {
            "category": self.categories[predicted_class],
            "confidence": combined_proba[predicted_class],
            "emotion": {
                "polarity": features["polarity"].iloc[0],
                "subjectivity": features["subjectivity"].iloc[0],
                "stress_score": features["stress_score"].iloc[0],
                "relaxation_score": features["relaxation_score"].iloc[0],
            },
        }

    def process_user_emails(
        self,
        username,
        maildir,
        email_count,
        max_emails,
        progress,
        overall_task,
        processed_count,
        emails,
        labels,
    ):
        """Helper function to process emails when using multithreaded loading"""
        user_start = processed_count[0]
        user_task = progress.add_task(
            f"[cyan]Processing user: {username}", total=email_count
        )

        # Process each folder in the maildir
        for folder in os.listdir(maildir):
            folder_path = os.path.join(maildir, folder)
            if not os.path.isdir(folder_path):
                continue

            # Map folder names to categories
            category_idx = -1
            for i, category in enumerate(self.categories):
                if category.lower() in folder.lower():
                    category_idx = i
                    break
            if category_idx == -1:
                if "sent" in folder.lower():
                    category_idx = 2  # Business
                elif "inbox" in folder.lower():
                    category_idx = 3  # Personal
                elif "deleted" in folder.lower():
                    category_idx = 5  # External
                else:
                    category_idx = 0  # Work

            # Process the folder
            self._process_folder(
                folder_path,
                category_idx,
                emails,
                labels,
                max_emails,
                progress=progress,
                task_id=user_task,
                overall_task=overall_task,
                processed_count=processed_count,
                username=username,
            )

            # If max_emails has been reached, break early
            if len(emails) >= max_emails:
                break

        user_processed = processed_count[0] - user_start
        return username, user_processed, email_count

    @staticmethod
    def serialize_prediction(
        email_id: str, prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Serialize model prediction results for storage.
        """
        return {
            "email_id": email_id,
            "category": prediction["category"],
            "confidence": prediction["confidence"],
            "polarity": prediction["emotion"]["polarity"],
            "subjectivity": prediction["emotion"]["subjectivity"],
            "stress_score": prediction["emotion"]["stress_score"],
            "relaxation_score": prediction["emotion"]["relaxation_score"],
        }
