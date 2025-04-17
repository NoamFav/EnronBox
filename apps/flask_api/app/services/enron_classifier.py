import pandas as pd
import numpy as np
import re
import os
import email
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from textblob import TextBlob

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
from rich.table import Table
from rich import box
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress NLTK download messages
import logging

logging.getLogger("nltk").setLevel(logging.ERROR)

from app.services.emotion_enhancer import EmotionEnhancer


class EnronEmailClassifier:
    def __init__(self):
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
        self.text_model = None
        self.numerical_model = None
        self.emotion_enhancer = EmotionEnhancer()

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

    def load_enron_emails(self, enron_dir, max_emails=5000):
        """Load and process emails from the Enron dataset using Rich progress tracking"""
        emails = []
        labels = []
        processed_count = [0]  # A mutable counter to track processed emails

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            # Estimate total emails and gather valid users
            total_estimated_emails = 0
            valid_users = []
            for username in os.listdir(enron_dir):
                user_dir = os.path.join(enron_dir, username)
                if not os.path.isdir(user_dir) or username.startswith("."):
                    continue

                maildir = os.path.join(user_dir, "maildir")
                if not os.path.exists(maildir) or not os.path.isdir(maildir):
                    maildir = user_dir

                user_email_count = sum(
                    len(files)
                    for root, _, files in os.walk(maildir)
                    if not root.endswith("attachments")
                )
                if user_email_count == 0:
                    continue

                total_estimated_emails += user_email_count
                valid_users.append((username, maildir, user_email_count))

            total_emails_to_process = min(total_estimated_emails, max_emails)
            overall_task = progress.add_task(
                "[bold green]📦 Processing Emails...",
                total=total_emails_to_process,
            )

            # Process each valid user
            for username, maildir, email_count in valid_users:
                user_dir = os.path.join(enron_dir, username)
                if not os.path.isdir(user_dir) or username.startswith("."):
                    continue

                if not os.path.exists(maildir) or not os.path.isdir(maildir):
                    maildir = user_dir

                # Record the overall processed count before starting this user
                user_start = processed_count[0]

                # Create a progress task for this user with the estimated total emails
                user_task = progress.add_task(
                    f"[cyan]Processing user: {username}", total=email_count
                )

                # Use the standard maildir if present
                user_maildir = os.path.join(user_dir, "maildir")
                if os.path.exists(user_maildir) and os.path.isdir(user_maildir):
                    maildir = user_maildir
                else:
                    maildir = user_dir

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

                # Compute the number of emails processed for this user
                user_processed = processed_count[0] - user_start

                # Create a descriptive message based on whether we processed all emails from the user
                if user_processed < email_count:
                    description_msg = (
                        f"[green]✅ Done processing {username} emails - max emails reached "
                        f"({user_processed}/{email_count})"
                    )
                else:
                    description_msg = f"[green]✅ Done processing {username} emails ({user_processed}/{email_count})"

                progress.update(
                    user_task,
                    completed=user_processed,
                    description=description_msg,
                )
                if len(emails) >= max_emails:
                    break

        if not emails:
            self._rich_print(
                f"No emails were loaded from {enron_dir}. Check the directory structure.",
                "bold red",
            )
            raise ValueError("No emails found in the specified directory.")

        email_df = pd.DataFrame(emails)

        summary_table = Table(
            title="📬 Email Dataset Summary",
            title_style="bold green",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold white on dark_blue",
            pad_edge=False,
        )

        summary_table.add_column(
            "📊 Metric", style="cyan", justify="left", no_wrap=True
        )
        summary_table.add_column("📈 Value", style="magenta", justify="left")

        summary_table.add_row("Total Emails", str(len(emails)))
        summary_table.add_row("Unique Categories", str(len(set(labels))))
        summary_table.add_row("Columns", ", ".join(email_df.columns.tolist()))

        self.console.print(summary_table)
        return email_df, np.array(labels)

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
                to = msg.get("To", "")
                cc = msg.get("Cc", "")
                num_recipients = 1
                if cc:
                    num_recipients += cc.count("@")
                try:
                    time_sent = pd.to_datetime(date_str)
                except:
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

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

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

        if missing_columns:
            print(f"Warning: Missing columns in email_data: {missing_columns}")
            for col in missing_columns:
                if col in ["body", "subject", "sender"]:
                    email_data[col] = ""
                elif col == "has_attachment":
                    email_data[col] = False
                elif col == "num_recipients":
                    email_data[col] = 1
                elif col == "time_sent":
                    email_data[col] = pd.Timestamp("2000-01-01")

        # Preprocess email body
        features["cleaned_text"] = email_data["body"].apply(self.preprocess_text)

        # Apply the EmotionEnhancer to each email body
        emotion_results = email_data["body"].apply(
            lambda text: self.emotion_enhancer.enhance_emotion_analysis(text)
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
            label_map = {label: i for i, label in enumerate(unique_labels)}
            mapped_labels = np.array([label_map[label] for label in labels])
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
            self.label_map = label_map
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
            save_path = os.path.join("results", "confusion_matrix.png")
            plt.savefig(save_path)
            self._rich_print(
                f"📊 Confusion Matrix saved at: {save_path}", style="bold yellow"
            )

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

            os.makedirs("results", exist_ok=True)
            importance_path = os.path.join("results", "feature_importance.png")
            plt.savefig(importance_path)
            self._rich_print(
                f"📸 Feature importance plot saved at: {importance_path}",
                style="bold yellow",
            )

        return self

    def predict(self, email):
        """Predict the category of a new email"""
        if self.text_model is None or self.numerical_model is None:
            raise Exception("Model not trained yet. Please train the model first.")

        # Convert single email to DataFrame format
        if isinstance(email, dict):
            email_df = pd.DataFrame([email])
        else:
            email_df = email

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
