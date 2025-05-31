from app.services.emotion_enhancer import EmotionEnhancer
from app.services.db import store_data
import sqlite3
import pandas as pd
import numpy as np
import re
import os
import pickle
import email
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Modern NLP imports
from transformers import (
    AutoTokenizer,
    AutoModel,
    AutoModelForSequenceClassification,
    pipeline,
)
import torch
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)


class EnronEmailClassifier:
    def __init__(self, model_dir="models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)

        # New category system from paste.txt
        self.categories = {
            "strategic_planning": {
                "name": "Strategic Planning",
                "description": "Long-term business strategy, corporate planning, acquisitions",
                "keywords": [
                    "strategy",
                    "planning",
                    "acquisition",
                    "merger",
                    "corporate",
                    "vision",
                    "roadmap",
                ],
            },
            "operational": {
                "name": "Daily Operations",
                "description": "Day-to-day operations, routine tasks, procedures",
                "keywords": [
                    "operations",
                    "daily",
                    "routine",
                    "procedure",
                    "process",
                    "workflow",
                ],
            },
            "financial": {
                "name": "Financial",
                "description": "Budget, accounting, financial reports, expenses",
                "keywords": [
                    "budget",
                    "financial",
                    "accounting",
                    "expense",
                    "revenue",
                    "cost",
                    "profit",
                ],
            },
            "legal_compliance": {
                "name": "Legal & Compliance",
                "description": "Legal matters, regulatory compliance, contracts",
                "keywords": [
                    "legal",
                    "compliance",
                    "regulation",
                    "contract",
                    "agreement",
                    "policy",
                ],
            },
            "client_external": {
                "name": "Client & External",
                "description": "External communications, client relations, partnerships",
                "keywords": [
                    "client",
                    "customer",
                    "external",
                    "partner",
                    "vendor",
                    "supplier",
                ],
            },
            "hr_personnel": {
                "name": "HR & Personnel",
                "description": "Human resources, hiring, employee matters",
                "keywords": [
                    "hr",
                    "hiring",
                    "employee",
                    "personnel",
                    "recruitment",
                    "performance",
                ],
            },
            "meetings_events": {
                "name": "Meetings & Events",
                "description": "Meeting scheduling, event planning, appointments",
                "keywords": [
                    "meeting",
                    "appointment",
                    "schedule",
                    "event",
                    "conference",
                    "calendar",
                ],
            },
            "urgent_critical": {
                "name": "Urgent & Critical",
                "description": "Time-sensitive, emergency, critical issues",
                "keywords": [
                    "urgent",
                    "emergency",
                    "critical",
                    "asap",
                    "immediate",
                    "deadline",
                ],
            },
            "personal_informal": {
                "name": "Personal & Informal",
                "description": "Personal communications, informal chats, non-work related",
                "keywords": [
                    "personal",
                    "informal",
                    "casual",
                    "chat",
                    "social",
                    "family",
                ],
            },
            "technical_it": {
                "name": "Technical & IT",
                "description": "Technical issues, IT support, system problems",
                "keywords": [
                    "technical",
                    "system",
                    "software",
                    "hardware",
                    "server",
                    "network",
                ],
            },
        }

        self.category_names = list(self.categories.keys())
        self.label_encoder = LabelEncoder()
        self.emotion_enhancer = EmotionEnhancer()

        # Initialize models
        self._initialize_models()
        self._load_models()

    def _initialize_models(self):
        """Initialize transformer models"""
        try:
            # Sentence transformer for embeddings
            self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

            # BERT tokenizer for text processing
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

            # Classification pipeline for zero-shot classification
            self.classifier_pipeline = pipeline(
                "zero-shot-classification",
                model="facebook/bart-base",
                device=0 if torch.cuda.is_available() else -1,
            )

        except Exception as e:
            print(f"Warning: Could not initialize all transformer models: {e}")
            self.sentence_model = None
            self.classifier_pipeline = None

    def _load_models(self):
        """Load pre-trained models if they exist"""
        model_path = self.model_dir / "email_classifier.pkl"

        if model_path.exists():
            try:
                with open(model_path, "rb") as f:
                    saved_data = pickle.load(f)
                    self.ensemble_model = saved_data.get("model")
                    self.label_encoder = saved_data.get(
                        "label_encoder", self.label_encoder
                    )
                print("Loaded pre-trained model")
            except Exception as e:
                print(f"Could not load model: {e}")
                self.ensemble_model = None
        else:
            self.ensemble_model = None

    def _save_models(self):
        """Save trained models"""
        model_path = self.model_dir / "email_classifier.pkl"

        try:
            with open(model_path, "wb") as f:
                pickle.dump(
                    {"model": self.ensemble_model, "label_encoder": self.label_encoder},
                    f,
                )
            print("Model saved successfully")
        except Exception as e:
            print(f"Could not save model: {e}")

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess email text"""
        if pd.isna(text) or not text:
            return ""

        text = str(text).lower()
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # Remove email addresses and URLs
        text = re.sub(r"\S+@\S+\.\S+", "[EMAIL]", text)
        text = re.sub(r"http\S+|www\S+", "[URL]", text)
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_embeddings(self, texts: List[str]) -> np.ndarray:
        """Extract sentence embeddings using transformer model"""
        if self.sentence_model is None:
            # Fallback to simple text features
            return self._extract_simple_features(texts)

        try:
            embeddings = self.sentence_model.encode(texts, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"Error extracting embeddings: {e}")
            return self._extract_simple_features(texts)

    def _extract_simple_features(self, texts: List[str]) -> np.ndarray:
        """Fallback feature extraction without transformers"""
        features = []
        for text in texts:
            text_features = [
                len(text),
                text.count("!"),
                text.count("?"),
                len(text.split()),
                (
                    1
                    if any(
                        word in text.lower() for word in ["urgent", "asap", "immediate"]
                    )
                    else 0
                ),
                (
                    1
                    if any(
                        word in text.lower()
                        for word in ["meeting", "schedule", "calendar"]
                    )
                    else 0
                ),
                (
                    1
                    if any(
                        word in text.lower() for word in ["budget", "financial", "cost"]
                    )
                    else 0
                ),
                (
                    1
                    if any(
                        word in text.lower()
                        for word in ["legal", "contract", "compliance"]
                    )
                    else 0
                ),
            ]
            features.append(text_features)

        return np.array(features)

    def extract_features(self, email_data: pd.DataFrame) -> np.ndarray:
        """Extract comprehensive features from email data"""
        # Combine subject and body
        combined_text = (
            email_data["subject"].fillna("").astype(str)
            + " "
            + email_data["body"].fillna("").astype(str)
        )

        # Preprocess text
        processed_texts = [self.preprocess_text(text) for text in combined_text]

        # Get embeddings
        text_embeddings = self.extract_embeddings(processed_texts)

        # Extract metadata features
        metadata_features = []
        for _, row in email_data.iterrows():
            # Get emotion analysis
            emotion_data = self.emotion_enhancer.enhance_emotion_analysis(
                str(row.get("body", ""))
            )

            meta_features = [
                len(str(row.get("subject", ""))),
                len(str(row.get("body", ""))),
                int(row.get("has_attachment", False)),
                row.get("num_recipients", 1),
                (
                    row.get("time_sent", pd.Timestamp("2000-01-01")).hour
                    if pd.notna(row.get("time_sent"))
                    else 12
                ),
                emotion_data.get("polarity", 0),
                emotion_data.get("subjectivity", 0),
                emotion_data.get("stress_score", 0),
                emotion_data.get("relaxation_score", 0),
            ]
            metadata_features.append(meta_features)

        metadata_features = np.array(metadata_features)

        # Combine embeddings and metadata
        if text_embeddings.shape[0] > 0:
            features = np.hstack([text_embeddings, metadata_features])
        else:
            features = metadata_features

        return features

    def classify_with_transformers(self, texts: List[str]) -> List[Dict]:
        """Use zero-shot classification with transformers"""
        if self.classifier_pipeline is None:
            return [{"category": "operational", "confidence": 0.5} for _ in texts]

        try:
            candidate_labels = [
                cat_data["name"] for cat_data in self.categories.values()
            ]
            results = []

            for text in texts:
                if not text.strip():
                    results.append({"category": "operational", "confidence": 0.5})
                    continue

                try:
                    prediction = self.classifier_pipeline(text, candidate_labels)
                    best_label = prediction["labels"][0]
                    confidence = prediction["scores"][0]

                    # Map back to category key
                    category_key = next(
                        (
                            key
                            for key, value in self.categories.items()
                            if value["name"] == best_label
                        ),
                        "operational",
                    )

                    results.append({"category": category_key, "confidence": confidence})
                except Exception as e:
                    print(f"Error in transformer classification: {e}")
                    results.append({"category": "operational", "confidence": 0.5})

            return results

        except Exception as e:
            print(f"Error in transformer pipeline: {e}")
            return [{"category": "operational", "confidence": 0.5} for _ in texts]

    def map_folder_to_category(self, folder_name: str) -> str:
        """Map folder names to categories using keyword matching"""
        folder_lower = folder_name.lower()

        # Direct keyword matching
        for category_key, category_data in self.categories.items():
            for keyword in category_data["keywords"]:
                if keyword in folder_lower:
                    return category_key

        # Fallback mapping
        if any(word in folder_lower for word in ["sent", "outbox"]):
            return "client_external"
        elif any(word in folder_lower for word in ["inbox", "received"]):
            return "operational"
        elif any(word in folder_lower for word in ["deleted", "trash"]):
            return "personal_informal"
        elif any(word in folder_lower for word in ["draft", "unsent"]):
            return "operational"
        else:
            return "operational"  # Default category

    def load_enron_emails(
        self, enron_db_path: str, max_emails: int = 5000
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Load emails from SQLite database"""
        conn = sqlite3.connect(enron_db_path)
        query = """
            SELECT
                e.id AS email_id,
                e.from_address AS sender,
                e.subject AS subject,
                e.body AS body,
                f.name AS folder_name,
                e.date AS time_sent
            FROM emails e
            JOIN folders f ON e.folder_id = f.id
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(max_emails,))
        conn.close()

        # Add missing columns
        df["has_attachment"] = False
        df["num_recipients"] = 1
        df["time_sent"] = pd.to_datetime(df["time_sent"], errors="coerce")

        # Map folders to categories
        labels = [self.map_folder_to_category(folder) for folder in df["folder_name"]]

        # Drop folder_name column
        df = df.drop(columns=["folder_name"])

        return df, np.array(labels)

    def train(self, email_data: pd.DataFrame, labels: np.ndarray):
        """Train the classifier with modern ensemble approach"""
        print("Training modern email classifier...")

        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)

        # Extract features
        print("Extracting features...")
        features = self.extract_features(email_data)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features,
            encoded_labels,
            test_size=0.2,
            random_state=42,
            stratify=encoded_labels,
        )

        # Create ensemble model
        print("Training ensemble model...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        lr_model = LogisticRegression(random_state=42, max_iter=1000)

        self.ensemble_model = VotingClassifier(
            estimators=[("rf", rf_model), ("lr", lr_model)], voting="soft"
        )

        self.ensemble_model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.ensemble_model.predict(X_test)

        # Convert back to category names for evaluation
        test_categories = self.label_encoder.inverse_transform(y_test)
        pred_categories = self.label_encoder.inverse_transform(y_pred)

        print("\nClassification Report:")
        print(classification_report(test_categories, pred_categories))

        # Save model
        self._save_models()

        return self

    def predict(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Predict category for a single email"""
        if self.ensemble_model is None:
            raise ValueError("Model not trained yet. Please train the model first.")

        # Convert to DataFrame
        if isinstance(message, dict):
            email_df = pd.DataFrame([message])
        else:
            email_df = message

        # Extract features
        features = self.extract_features(email_df)

        # Get ensemble prediction
        prediction_proba = self.ensemble_model.predict_proba(features)[0]
        predicted_class = np.argmax(prediction_proba)
        confidence = prediction_proba[predicted_class]

        # Get category name
        category_key = self.label_encoder.inverse_transform([predicted_class])[0]

        # Get emotion analysis
        emotion_data = self.emotion_enhancer.enhance_emotion_analysis(
            str(message.get("body", ""))
        )

        # Try transformer classification as additional signal
        combined_text = f"{message.get('subject', '')} {message.get('body', '')}"
        transformer_results = self.classify_with_transformers([combined_text])

        return {
            "category": category_key,
            "category_name": self.categories[category_key]["name"],
            "confidence": float(confidence),
            "transformer_category": transformer_results[0]["category"],
            "transformer_confidence": transformer_results[0]["confidence"],
            "emotion": {
                "polarity": emotion_data.get("polarity", 0),
                "subjectivity": emotion_data.get("subjectivity", 0),
                "stress_score": emotion_data.get("stress_score", 0),
                "relaxation_score": emotion_data.get("relaxation_score", 0),
            },
        }

    @staticmethod
    def serialize_prediction(
        email_id: str, prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Serialize prediction results for storage"""
        return {
            "email_id": email_id,
            "category": prediction["category"],
            "category_name": prediction["category_name"],
            "confidence": prediction["confidence"],
            "transformer_category": prediction.get("transformer_category", ""),
            "transformer_confidence": prediction.get("transformer_confidence", 0.0),
            "polarity": prediction["emotion"]["polarity"],
            "subjectivity": prediction["emotion"]["subjectivity"],
            "stress_score": prediction["emotion"]["stress_score"],
            "relaxation_score": prediction["emotion"]["relaxation_score"],
        }
