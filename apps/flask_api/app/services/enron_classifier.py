from app.services.emotion_enhancer import EmotionEnhancer
import sqlite3
import pandas as pd
import numpy as np
import re
import pickle
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging

# Modern NLP imports
from transformers import (
    AutoTokenizer,
    pipeline,
)
import torch
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
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
        if pd.isna(folder_name) or not folder_name:
            return "operational"

        folder_lower = folder_name.lower().strip()

        # Enhanced keyword matching with more comprehensive patterns
        folder_mappings = {
            "strategic_planning": [
                "strategy",
                "strategic",
                "planning",
                "acquisition",
                "merger",
                "corporate",
                "vision",
                "roadmap",
                "business_plan",
                "growth",
            ],
            "operational": [
                "operations",
                "daily",
                "routine",
                "procedure",
                "process",
                "workflow",
                "inbox",
                "received",
                "general",
                "main",
                "default",
            ],
            "financial": [
                "budget",
                "financial",
                "accounting",
                "expense",
                "revenue",
                "cost",
                "profit",
                "finance",
                "money",
                "payment",
                "invoice",
            ],
            "legal_compliance": [
                "legal",
                "compliance",
                "regulation",
                "contract",
                "agreement",
                "policy",
                "law",
                "regulatory",
                "audit",
                "risk",
            ],
            "client_external": [
                "client",
                "customer",
                "external",
                "partner",
                "vendor",
                "supplier",
                "sent",
                "outbox",
                "public",
                "marketing",
            ],
            "hr_personnel": [
                "hr",
                "hiring",
                "employee",
                "personnel",
                "recruitment",
                "performance",
                "human",
                "staff",
                "team",
                "people",
            ],
            "meetings_events": [
                "meeting",
                "appointment",
                "schedule",
                "event",
                "conference",
                "calendar",
                "agenda",
                "meeting_notes",
                "call",
            ],
            "urgent_critical": [
                "urgent",
                "emergency",
                "critical",
                "asap",
                "immediate",
                "deadline",
                "priority",
                "important",
                "alert",
            ],
            "personal_informal": [
                "personal",
                "informal",
                "casual",
                "chat",
                "social",
                "family",
                "deleted",
                "trash",
                "private",
                "personal_notes",
            ],
            "technical_it": [
                "technical",
                "system",
                "software",
                "hardware",
                "server",
                "network",
                "it",
                "tech",
                "computer",
                "database",
            ],
        }

        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in folder_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in folder_lower:
                    # Give higher score for exact matches
                    if keyword == folder_lower:
                        score += 10
                    # Give medium score for word boundaries
                    elif (
                        f"_{keyword}_" in f"_{folder_lower}_"
                        or f" {keyword} " in f" {folder_lower} "
                    ):
                        score += 5
                    # Give lower score for partial matches
                    else:
                        score += 1
            category_scores[category] = score

        # Find the best matching category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:  # Only return if there's at least one match
                return best_category[0]

        # Enhanced fallback logic
        if any(word in folder_lower for word in ["sent", "outbox", "out"]):
            return "client_external"
        elif any(word in folder_lower for word in ["inbox", "received", "in"]):
            return "operational"
        elif any(word in folder_lower for word in ["deleted", "trash", "delete"]):
            return "personal_informal"
        elif any(word in folder_lower for word in ["draft", "unsent", "temp"]):
            return "operational"
        elif any(word in folder_lower for word in ["archive", "old", "backup"]):
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

        # Print label distribution for debugging
        from collections import Counter

        label_counts = Counter(labels)
        print(f"Label distribution: {dict(label_counts)}")

        # Filter out categories with very few samples (less than 2)
        min_samples = 2
        valid_indices = []
        filtered_labels = []

        for i, label in enumerate(labels):
            if label_counts[label] >= min_samples:
                valid_indices.append(i)
                filtered_labels.append(label)

        if len(valid_indices) < len(labels):
            print(
                f"Filtering out {len(labels) - len(valid_indices)} samples from categories with < {min_samples} samples"
            )
            email_data = email_data.iloc[valid_indices].reset_index(drop=True)
            labels = np.array(filtered_labels)

            # Update label counts after filtering
            label_counts = Counter(labels)
            print(f"Filtered label distribution: {dict(label_counts)}")

        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)

        # Extract features
        print("Extracting features...")
        features = self.extract_features(email_data)

        # Check if we have enough samples for stratified split
        unique_labels, label_counts = np.unique(encoded_labels, return_counts=True)
        min_count = np.min(label_counts)

        if min_count < 2:
            print(
                f"Warning: Some classes still have only {min_count} sample(s). Using random split instead of stratified."
            )
            # Use random split without stratification
            X_train, X_test, y_train, y_test = train_test_split(
                features,
                encoded_labels,
                test_size=0.2,
                random_state=42,
                # Remove stratify parameter
            )
        else:
            # Use stratified split
            X_train, X_test, y_train, y_test = train_test_split(
                features,
                encoded_labels,
                test_size=0.2,
                random_state=42,
                stratify=encoded_labels,
            )

        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")

        # Create ensemble model
        print("Training ensemble model...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",  # Handle class imbalance
        )
        lr_model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            class_weight="balanced",  # Handle class imbalance
        )

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
        print(classification_report(test_categories, pred_categories, zero_division=0))

        # Print final model info
        print(
            f"\nModel trained on {len(features)} emails across {len(unique_labels)} categories"
        )
        print(f"Categories: {list(self.label_encoder.classes_)}")

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

    def analyze_dataset(
        self, email_data: pd.DataFrame, labels: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze the dataset to identify potential training issues"""
        from collections import Counter
        import matplotlib.pyplot as plt

        analysis = {}

        # Basic statistics
        analysis["total_emails"] = len(labels)
        analysis["total_categories"] = len(set(labels))

        # Label distribution
        label_counts = Counter(labels)
        analysis["label_distribution"] = dict(label_counts)

        # Categories with insufficient samples
        min_samples_needed = 2
        insufficient_categories = {
            k: v for k, v in label_counts.items() if v < min_samples_needed
        }
        analysis["insufficient_categories"] = insufficient_categories
        analysis["categories_to_filter"] = len(insufficient_categories)

        # Data quality checks
        null_subjects = email_data["subject"].isna().sum()
        null_bodies = email_data["body"].isna().sum()
        empty_subjects = (email_data["subject"].str.strip() == "").sum()
        empty_bodies = (email_data["body"].str.strip() == "").sum()

        analysis["data_quality"] = {
            "null_subjects": int(null_subjects),
            "null_bodies": int(null_bodies),
            "empty_subjects": int(empty_subjects),
            "empty_bodies": int(empty_bodies),
            "emails_with_content": int(
                len(email_data)
                - max(null_subjects + empty_subjects, null_bodies + empty_bodies)
            ),
        }

        # Text length statistics
        combined_text = (
            email_data["subject"].fillna("").astype(str)
            + " "
            + email_data["body"].fillna("").astype(str)
        )
        text_lengths = [len(text) for text in combined_text]

        analysis["text_statistics"] = {
            "avg_text_length": float(np.mean(text_lengths)),
            "median_text_length": float(np.median(text_lengths)),
            "min_text_length": int(np.min(text_lengths)),
            "max_text_length": int(np.max(text_lengths)),
            "very_short_emails": int(sum(1 for length in text_lengths if length < 50)),
            "very_long_emails": int(sum(1 for length in text_lengths if length > 5000)),
        }

        # Recommendations
        recommendations = []

        if len(insufficient_categories) > 0:
            recommendations.append(
                f"Filter out {len(insufficient_categories)} categories with < {min_samples_needed} samples"
            )

        if analysis["data_quality"]["emails_with_content"] < len(email_data) * 0.8:
            recommendations.append("Consider filtering emails with very little content")

        if analysis["text_statistics"]["very_short_emails"] > len(email_data) * 0.1:
            recommendations.append(
                "Many emails are very short - consider combining subject and body text"
            )

        analysis["recommendations"] = recommendations

        return analysis

    def print_dataset_analysis(self, analysis: Dict[str, Any]):
        """Print a formatted dataset analysis report"""
        print("=" * 60)
        print("DATASET ANALYSIS REPORT")
        print("=" * 60)

        print(f"\n📊 BASIC STATISTICS")
        print(f"Total emails: {analysis['total_emails']:,}")
        print(f"Total categories: {analysis['total_categories']}")

        print(f"\n📈 CATEGORY DISTRIBUTION")
        sorted_categories = sorted(
            analysis["label_distribution"].items(), key=lambda x: x[1], reverse=True
        )
        for category, count in sorted_categories:
            print(f"  {category}: {count:,} emails")

        if analysis["insufficient_categories"]:
            print(f"\n⚠️  CATEGORIES WITH INSUFFICIENT SAMPLES (< 2)")
            for category, count in analysis["insufficient_categories"].items():
                print(f"  {category}: {count} email(s)")

        print(f"\n🔍 DATA QUALITY")
        dq = analysis["data_quality"]
        print(f"  Null subjects: {dq['null_subjects']:,}")
        print(f"  Null bodies: {dq['null_bodies']:,}")
        print(f"  Empty subjects: {dq['empty_subjects']:,}")
        print(f"  Empty bodies: {dq['empty_bodies']:,}")
        print(f"  Emails with content: {dq['emails_with_content']:,}")

        print(f"\n📝 TEXT STATISTICS")
        ts = analysis["text_statistics"]
        print(f"  Average text length: {ts['avg_text_length']:.1f} characters")
        print(f"  Median text length: {ts['median_text_length']:.1f} characters")
        print(
            f"  Text length range: {ts['min_text_length']} - {ts['max_text_length']} characters"
        )
        print(f"  Very short emails (< 50 chars): {ts['very_short_emails']:,}")
        print(f"  Very long emails (> 5000 chars): {ts['very_long_emails']:,}")

        if analysis["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(analysis["recommendations"], 1):
                print(f"  {i}. {rec}")

        print("=" * 60)
