import pandas as pd
import numpy as np
import re
import nltk
import os
import email
from email.parser import Parser
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

# Download necessary NLTK resources
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)


class EnronEmailClassifier:
    def __init__(self):
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

    def load_enron_emails(self, enron_dir, max_emails=10000):
        """Load and process emails from the Enron dataset using the standard structure"""
        emails = []
        labels = []
        
        print(f"Loading emails from: {enron_dir}")
        
        # Standard Enron structure has usernames at the top level
        for username in os.listdir(enron_dir):
            user_dir = os.path.join(enron_dir, username)
            
            # Skip if not a directory or if it's a hidden file
            if not os.path.isdir(user_dir) or username.startswith('.'):
                continue
                
            print(f"Processing user: {username}")
            
            # The standard structure has a maildir directory inside each user directory
            maildir = os.path.join(user_dir, "maildir")
            if not os.path.exists(maildir) or not os.path.isdir(maildir):
                # Some datasets might have the folders directly in the user directory
                maildir = user_dir
            
            # Process each folder (these represent categories like "sent", "inbox", etc.)
            for folder in os.listdir(maildir):
                folder_path = os.path.join(maildir, folder)
                
                if not os.path.isdir(folder_path):
                    continue
                    
                print(f"  Processing folder: {folder}")
                
                # Map folder names to categories
                category_idx = -1
                for i, category in enumerate(self.categories):
                    if category.lower() in folder.lower():
                        category_idx = i
                        break
                
                # If not matched to predefined categories, use a default
                if category_idx == -1:
                    if "sent" in folder.lower():
                        category_idx = 2  # Business
                    elif "inbox" in folder.lower():
                        category_idx = 3  # Personal
                    elif "deleted" in folder.lower():
                        category_idx = 5  # External
                    else:
                        category_idx = 0  # Work
                
                # Process emails in this folder and any subfolders
                self._process_folder(folder_path, category_idx, emails, labels, max_emails)
                
                if len(emails) >= max_emails:
                    print(f"Reached maximum number of emails: {max_emails}")
                    break
            
            if len(emails) >= max_emails:
                break
        
        if not emails:
            raise ValueError(f"No emails were loaded from {enron_dir}. Check the directory structure.")
        
        # Convert to DataFrame
        email_df = pd.DataFrame(emails)
        print(f"Loaded {len(emails)} emails with {len(set(labels))} different categories")
        print(f"Columns in DataFrame: {email_df.columns.tolist()}")
        print(f"First few rows: {email_df.head()}")
        
        return email_df, np.array(labels)
    
    def _process_folder(self, folder_path, category_idx, emails, labels, max_emails):
        """Process all emails in a folder and its subfolders"""
        # Process files in the current folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # If this is a subfolder, process it recursively
            if os.path.isdir(file_path):
                self._process_folder(file_path, category_idx, emails, labels, max_emails)
                continue
            
            # Skip if we've reached the max emails
            if len(emails) >= max_emails:
                return
            
            # Process the email file
            try:
                # Parse the email file
                with open(file_path, 'r', encoding='latin1', errors='ignore') as f:
                    msg_content = f.read()
                
                # Parse using the email module
                msg = email.message_from_string(msg_content)
                
                # Extract basic fields
                subject = msg.get('Subject', '')
                sender = msg.get('From', '')
                date_str = msg.get('Date', '')
                to = msg.get('To', '')
                cc = msg.get('Cc', '')
                
                # Count recipients
                num_recipients = 1  # Assume at least one recipient
                if cc:
                    num_recipients += cc.count('@')
                
                # Convert date string to timestamp
                try:
                    time_sent = pd.to_datetime(date_str)
                except:
                    time_sent = pd.Timestamp('2000-01-01')
                
                # Extract body
                body = self._extract_email_body(msg)
                
                # Check for attachments
                has_attachment = False
                for part in msg.walk():
                    if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition'):
                        has_attachment = True
                        break
                
                # Add email to dataset
                emails.append({
                    'subject': subject,
                    'body': body,
                    'sender': sender,
                    'has_attachment': has_attachment,
                    'num_recipients': num_recipients,
                    'time_sent': time_sent
                })
                
                # Add the corresponding label
                labels.append(category_idx)
                
                if len(emails) % 100 == 0:
                    print(f"Processed {len(emails)} emails...")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    def _extract_email_body(self, msg):
        """Extract the body text from an email message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                # Skip attachments
                if 'attachment' in content_disposition:
                    continue
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        if isinstance(payload, bytes):
                            body += payload.decode('latin1', errors='ignore')
                        else:
                            body += str(payload)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                if isinstance(payload, bytes):
                    body = payload.decode('latin1', errors='ignore')
                else:
                    body = str(payload)
        
        return body

    def extract_features(self, email_data):
        """Extract features from emails including emotion metrics"""
        features = pd.DataFrame()
        
        # Check if required columns exist
        required_columns = ['body', 'subject', 'sender', 'has_attachment', 'num_recipients', 'time_sent']
        missing_columns = [col for col in required_columns if col not in email_data.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns in email_data: {missing_columns}")
            for col in missing_columns:
                if col in ['body', 'subject', 'sender']:
                    email_data[col] = ""
                elif col == 'has_attachment':
                    email_data[col] = False
                elif col == 'num_recipients':
                    email_data[col] = 1
                elif col == 'time_sent':
                    email_data[col] = pd.Timestamp('2000-01-01')

        # Preprocess email body
        features["cleaned_text"] = email_data["body"].apply(self.preprocess_text)

        # Extract emotional features using TextBlob
        features["polarity"] = email_data["body"].apply(
            lambda text: (
                TextBlob(str(text)).sentiment.polarity
                if not isinstance(text, float)
                else 0
            )
        )
        features["subjectivity"] = email_data["body"].apply(
            lambda text: (
                TextBlob(str(text)).sentiment.subjectivity
                if not isinstance(text, float)
                else 0
            )
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

        # Check for excessive punctuation (common in spam)
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

    def train(self, email_data, labels):
        """Train the email classifier model"""
        # Print diagnostic info
        print("Training model with data shape:", email_data.shape)
        print("Available columns:", email_data.columns.tolist())
        
        # Extract features
        features = self.extract_features(email_data)
        print("Features extracted, shape:", features.shape)

        # Make sure labels are integers from 0 to n_classes-1
        unique_labels = np.unique(labels)
        n_classes = len(unique_labels)
        label_map = {label: i for i, label in enumerate(unique_labels)}
        mapped_labels = np.array([label_map[label] for label in labels])

        # Update the categories based on the labels we've seen
        self.categories = [
            self.categories[label] if label < len(self.categories) else f"Class_{label}"
            for label in unique_labels
        ]

        # Split the dataset
        X_train, X_test, y_train, y_test = train_test_split(
            features, mapped_labels, test_size=0.2, random_state=42
        )

        # Create text processing pipeline for cleaned_text
        text_pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=5000)),
                (
                    "classifier",
                    RandomForestClassifier(n_estimators=100, random_state=42),
                ),
            ]
        )

        # Extract the cleaned_text series for training
        train_text = X_train["cleaned_text"].values
        test_text = X_test["cleaned_text"].values

        # Train the model on text
        text_pipeline.fit(train_text, y_train)

        # Train another model on the numerical features
        numerical_features = X_train.drop(columns=["cleaned_text"])
        numerical_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        numerical_classifier.fit(numerical_features, y_train)

        # Store the models
        self.text_model = text_pipeline
        self.numerical_model = numerical_classifier
        self.label_map = label_map  # Store the label mapping

        # Evaluate the model
        text_predictions = text_pipeline.predict(test_text)
        numerical_predictions = numerical_classifier.predict(
            X_test.drop(columns=["cleaned_text"])
        )

        # Get probabilities
        text_proba = text_pipeline.predict_proba(test_text)
        numerical_proba = numerical_classifier.predict_proba(
            X_test.drop(columns=["cleaned_text"])
        )

        # Combine predictions (simple averaging)
        combined_proba = (text_proba + numerical_proba) / 2
        combined_predictions = np.argmax(combined_proba, axis=1)

        # Map numeric predictions back to category labels
        predicted_categories = [self.categories[i] for i in combined_predictions]
        actual_categories = [self.categories[i] for i in y_test]

        print(f"Classes: {self.categories}")
        print(f"Number of classes: {n_classes}")

        # Print classification report
        print("\nClassification Report:")
        print(classification_report(actual_categories, predicted_categories))

        # Generate confusion matrix
        if len(np.unique(actual_categories)) > 1:
            cm = confusion_matrix(
                actual_categories, predicted_categories, labels=self.categories
            )
            plt.figure(figsize=(10, 8))
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
            plt.savefig("confusion_matrix.png")  # Save plot to file
            plt.show()

        # Feature importance analysis
        if hasattr(self.numerical_model, "feature_importances_"):
            feature_names = numerical_features.columns
            importances = self.numerical_model.feature_importances_
            indices = np.argsort(importances)[::-1]

            plt.figure(figsize=(10, 6))
            plt.title("Feature Importances")
            plt.bar(range(len(indices)), importances[indices], align="center")
            plt.xticks(
                range(len(indices)), [feature_names[i] for i in indices], rotation=90
            )
            plt.tight_layout()
            plt.savefig("feature_importances.png")  # Save plot to file
            plt.show()

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
        numerical_proba = self.numerical_model.predict_proba(
            features.drop(columns=["cleaned_text"]).iloc[0:1]
        )[0]

        # Combine predictions
        combined_proba = (text_proba + numerical_proba) / 2
        predicted_class = np.argmax(combined_proba)

        # Return category and confidence
        return {
            "category": self.categories[predicted_class],
            "confidence": combined_proba[predicted_class],
            "emotion": {
                "polarity": features["polarity"].iloc[0],
                "subjectivity": features["subjectivity"].iloc[0],
            },
        }


# Example usage
if __name__ == "__main__":
    # Path to the Enron email dataset
    enron_dir = "./maildir"

    # Check if the directory exists
    if not os.path.exists(enron_dir):
        print(f"Error: Enron dataset directory '{enron_dir}' not found.")
        print("Please download the Enron dataset from https://www.cs.cmu.edu/~enron/")
        print(
            "or use a subset from https://www.kaggle.com/datasets/wcukierski/enron-email-dataset"
        )
        exit(1)

    # Initialize the classifier
    classifier = EnronEmailClassifier()

    # Load the Enron emails (limit to 5000 for faster processing)
    email_df, labels = classifier.load_enron_emails(enron_dir, max_emails=5000)
    
    # Save the loaded data to CSV for inspection
    email_df.to_csv("enron_emails.csv", index=False)
    print(f"Saved {len(email_df)} emails to 'enron_emails.csv'")

    # Print information about the loaded data
    print(f"Loaded {len(email_df)} emails with {len(np.unique(labels))} unique labels")
    print(f"Label distribution: {np.bincount(labels.astype(int))}")

    # Train the classifier
    classifier.train(email_df, labels)

    # Example new email for testing
    new_email = {
        "subject": "Meeting tomorrow at 10 AM",
        "body": "We will discuss the upcoming project timeline in the meeting tomorrow.",
        "sender": "colleague@enron.com",
        "has_attachment": True,
        "num_recipients": 3,
        "time_sent": pd.Timestamp("2001-01-02 16:45"),
    }

    # Predict the category
    prediction = classifier.predict(new_email)
    print(f"\nPrediction for new email:")
    print(f"Predicted category: {prediction['category']}")
    print(f"Confidence: {prediction['confidence']:.2f}")
    print(
        f"Email emotion - Polarity: {prediction['emotion']['polarity']:.2f}, Subjectivity: {prediction['emotion']['subjectivity']:.2f}"
    )