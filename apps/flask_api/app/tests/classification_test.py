#!/usr/bin/env python3
"""
Comprehensive test suite for EnronEmailClassifier performance evaluation.
Tests training, prediction accuracy, and provides detailed analysis.
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Any
import time
from datetime import datetime
from collections import Counter, defaultdict
import warnings
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support,
    balanced_accuracy_score,
)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Add the parent directory to path to import the classifier
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock the EmotionEnhancer since it's not provided
class MockEmotionEnhancer:
    def enhance_emotion_analysis(self, text: str) -> Dict[str, float]:
        """Mock emotion analysis that returns random but consistent values"""
        import hashlib

        # Use hash for consistent results across runs
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        np.random.seed(text_hash % 2**32)
        return {
            "polarity": np.random.uniform(-1, 1),
            "subjectivity": np.random.uniform(0, 1),
            "stress_score": np.random.uniform(0, 1),
            "relaxation_score": np.random.uniform(0, 1),
        }


# Mock the app.services.emotion_enhancer module
class MockModule:
    def __init__(self):
        self.EmotionEnhancer = MockEmotionEnhancer


sys.modules["app.services.emotion_enhancer"] = MockModule()

# Now import the classifier
try:
    from app.services.enron_classifier import EnronEmailClassifier
except ImportError as e:
    print(f"Error importing EnronEmailClassifier: {e}")
    print(
        "Make sure the classifier code is in a file named 'paste.py' in the same directory"
    )
    sys.exit(1)


class EnronClassifierTester:
    """Comprehensive test suite for EnronEmailClassifier"""

    def __init__(self, db_path: str = "../SQLite_db/enron.db"):
        self.db_path = db_path
        self.classifier = None
        self.test_results = {}
        self.training_time = 0
        self.prediction_times = []

        # Create results directory
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)

        print(f"🧪 EnronEmailClassifier Test Suite")
        print(f"Database: {db_path}")
        print(f"Results will be saved to: {self.results_dir}")
        print("=" * 60)

    def check_database(self) -> bool:
        """Verify database exists and has expected structure"""
        print("🔍 Checking database...")

        if not os.path.exists(self.db_path):
            print(f"❌ Database not found at {self.db_path}")
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ["users", "folders", "emails", "email_classifications"]

            missing_tables = [t for t in expected_tables if t not in tables]
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False

            # Check email count
            cursor.execute("SELECT COUNT(*) FROM emails;")
            email_count = cursor.fetchone()[0]

            print(f"✅ Database OK - {email_count:,} emails found")
            conn.close()
            return True

        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

    def analyze_database_content(self) -> Dict[str, Any]:
        """Analyze the database content for insights"""
        print("\n📊 Analyzing database content...")

        conn = sqlite3.connect(self.db_path)

        # Get email statistics
        query = """
        SELECT
            COUNT(*) as total_emails,
            COUNT(DISTINCT f.name) as unique_folders,
            AVG(LENGTH(e.subject)) as avg_subject_length,
            AVG(LENGTH(e.body)) as avg_body_length,
            COUNT(CASE WHEN e.subject IS NULL OR e.subject = '' THEN 1 END) as empty_subjects,
            COUNT(CASE WHEN e.body IS NULL OR e.body = '' THEN 1 END) as empty_bodies
        FROM emails e
        JOIN folders f ON e.folder_id = f.id
        """

        stats = pd.read_sql_query(query, conn).iloc[0].to_dict()

        # Get folder distribution
        folder_query = """
        SELECT f.name as folder_name, COUNT(*) as email_count
        FROM emails e
        JOIN folders f ON e.folder_id = f.id
        GROUP BY f.name
        ORDER BY email_count DESC
        LIMIT 20
        """

        folder_dist = pd.read_sql_query(folder_query, conn)

        # Get sample emails for each major folder
        sample_query = """
        SELECT f.name as folder_name, e.subject,
               SUBSTR(e.body, 1, 100) as body_sample
        FROM emails e
        JOIN folders f ON e.folder_id = f.id
        WHERE f.name IN (
            SELECT f2.name
            FROM emails e2
            JOIN folders f2 ON e2.folder_id = f2.id
            GROUP BY f2.name
            ORDER BY COUNT(*) DESC
            LIMIT 10
        )
        GROUP BY f.name
        HAVING COUNT(*) > 0
        ORDER BY f.name
        """

        samples = pd.read_sql_query(sample_query, conn)
        conn.close()

        analysis = {
            "statistics": stats,
            "folder_distribution": folder_dist,
            "folder_samples": samples,
        }

        # Print analysis
        print(f"  Total emails: {stats['total_emails']:,}")
        print(f"  Unique folders: {stats['unique_folders']}")
        print(f"  Avg subject length: {stats['avg_subject_length']:.1f} chars")
        print(f"  Avg body length: {stats['avg_body_length']:.1f} chars")
        print(f"  Empty subjects: {stats['empty_subjects']:,}")
        print(f"  Empty bodies: {stats['empty_bodies']:,}")

        print("\n📁 Top 10 folder distributions:")
        for _, row in folder_dist.head(10).iterrows():
            print(f"  {row['folder_name']}: {row['email_count']:,} emails")

        return analysis

    def test_classifier_initialization(self) -> bool:
        """Test classifier initialization and model loading"""
        print("\n🚀 Testing classifier initialization...")

        try:
            start_time = time.time()
            self.classifier = EnronEmailClassifier(model_dir="test_models")
            init_time = time.time() - start_time

            print(f"✅ Classifier initialized in {init_time:.2f}s")
            print(f"  Device: {self.classifier.device}")
            print(f"  Categories: {len(self.classifier.categories)}")
            print(
                f"  Sentence model loaded: {self.classifier.sentence_model is not None}"
            )
            print(
                f"  Classification pipeline loaded: {self.classifier.classifier_pipeline is not None}"
            )

            return True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def test_training(self, max_emails: int = 5000) -> bool:
        """Test model training with various dataset sizes"""
        print(f"\n🎯 Testing training with {max_emails:,} emails...")

        try:
            # Load data
            print("📥 Loading training data...")
            email_data, labels = self.classifier.load_enron_emails(
                self.db_path, max_emails=max_emails
            )

            print(f"  Loaded {len(email_data):,} emails")
            print(f"  Categories found: {len(set(labels))}")

            # Analyze dataset before training
            analysis = self.classifier.analyze_dataset(email_data, labels)
            self.classifier.print_dataset_analysis(analysis)

            # Train model
            print("\n🏋️ Training model...")
            start_time = time.time()
            self.classifier.train(email_data, labels)
            self.training_time = time.time() - start_time

            print(f"✅ Training completed in {self.training_time:.2f}s")
            print(
                f"  Training rate: {len(email_data)/self.training_time:.1f} emails/second"
            )

            return True

        except Exception as e:
            print(f"❌ Training failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def test_predictions(self, num_samples: int = 100) -> Dict[str, Any]:
        """Test prediction accuracy on a sample of emails"""
        print(f"\n🎲 Testing predictions on {num_samples} samples...")

        if self.classifier is None or self.classifier.ensemble_model is None:
            print("❌ No trained model available")
            return {}

        try:
            # Load test data
            conn = sqlite3.connect(self.db_path)
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
            ORDER BY RANDOM()
            LIMIT ?
            """

            test_data = pd.read_sql_query(query, conn, params=(num_samples,))
            conn.close()

            # Add required columns
            test_data["has_attachment"] = False
            test_data["num_recipients"] = 1
            test_data["time_sent"] = pd.to_datetime(
                test_data["time_sent"], errors="coerce"
            )

            # Get true labels using folder mapping
            true_labels = [
                self.classifier.map_folder_to_category(folder)
                for folder in test_data["folder_name"]
            ]

            # Make predictions
            print("🔮 Making predictions...")
            predictions = []
            prediction_times = []

            for idx, row in test_data.iterrows():
                email_dict = {
                    "subject": row["subject"],
                    "body": row["body"],
                    "sender": row["sender"],
                    "has_attachment": row["has_attachment"],
                    "num_recipients": row["num_recipients"],
                    "time_sent": row["time_sent"],
                }

                start_time = time.time()
                prediction = self.classifier.predict(email_dict)
                pred_time = time.time() - start_time

                predictions.append(prediction)
                prediction_times.append(pred_time)

                if (idx + 1) % 20 == 0:
                    print(f"  Processed {idx + 1}/{num_samples} emails...")

            predicted_labels = [pred["category"] for pred in predictions]
            confidences = [pred["confidence"] for pred in predictions]

            # Calculate metrics
            accuracy = accuracy_score(true_labels, predicted_labels)
            balanced_acc = balanced_accuracy_score(true_labels, predicted_labels)

            # Per-category metrics
            precision, recall, f1, support = precision_recall_fscore_support(
                true_labels, predicted_labels, average=None, zero_division=0
            )

            # Get unique categories
            categories = sorted(list(set(true_labels + predicted_labels)))

            results = {
                "accuracy": accuracy,
                "balanced_accuracy": balanced_acc,
                "avg_confidence": np.mean(confidences),
                "avg_prediction_time": np.mean(prediction_times),
                "total_prediction_time": sum(prediction_times),
                "predictions_per_second": len(predictions) / sum(prediction_times),
                "true_labels": true_labels,
                "predicted_labels": predicted_labels,
                "confidences": confidences,
                "categories": categories,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": support,
                "test_data": test_data,
                "predictions": predictions,
            }

            print(f"✅ Prediction testing completed")
            print(f"  Overall accuracy: {accuracy:.3f}")
            print(f"  Balanced accuracy: {balanced_acc:.3f}")
            print(f"  Average confidence: {np.mean(confidences):.3f}")
            print(
                f"  Prediction speed: {results['predictions_per_second']:.1f} emails/second"
            )

            return results

        except Exception as e:
            print(f"❌ Prediction testing failed: {e}")
            import traceback

            traceback.print_exc()
            return {}

    def generate_confusion_matrix(self, results: Dict[str, Any]) -> None:
        """Generate and save confusion matrix visualization"""
        if not results:
            return

        print("\n📈 Generating confusion matrix...")

        # Create confusion matrix
        cm = confusion_matrix(results["true_labels"], results["predicted_labels"])
        categories = results["categories"]

        # Plot confusion matrix
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=categories,
            yticklabels=categories,
        )
        plt.title("Email Classification Confusion Matrix")
        plt.xlabel("Predicted Category")
        plt.ylabel("True Category")
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()

        # Save plot
        confusion_path = self.results_dir / "confusion_matrix.png"
        plt.savefig(confusion_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"  Confusion matrix saved to {confusion_path}")

    def generate_performance_report(self, results: Dict[str, Any]) -> None:
        """Generate detailed performance report"""
        if not results:
            return

        print("\n📊 Generating performance report...")

        # Classification report
        report = classification_report(
            results["true_labels"],
            results["predicted_labels"],
            target_names=results["categories"],
            zero_division=0,
            output_dict=True,
        )

        # Create detailed report
        report_content = []
        report_content.append("ENRON EMAIL CLASSIFIER PERFORMANCE REPORT")
        report_content.append("=" * 60)
        report_content.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_content.append(f"Test samples: {len(results['true_labels'])}")
        report_content.append("")

        # Overall metrics
        report_content.append("OVERALL PERFORMANCE")
        report_content.append("-" * 30)
        report_content.append(f"Accuracy: {results['accuracy']:.3f}")
        report_content.append(f"Balanced Accuracy: {results['balanced_accuracy']:.3f}")
        report_content.append(f"Average Confidence: {results['avg_confidence']:.3f}")
        report_content.append(f"Training Time: {self.training_time:.2f}s")
        report_content.append(
            f"Avg Prediction Time: {results['avg_prediction_time']*1000:.1f}ms"
        )
        report_content.append(
            f"Predictions/Second: {results['predictions_per_second']:.1f}"
        )
        report_content.append("")

        # Per-category performance
        report_content.append("PER-CATEGORY PERFORMANCE")
        report_content.append("-" * 40)
        report_content.append(
            f"{'Category':<20} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<10}"
        )
        report_content.append("-" * 70)

        for i, category in enumerate(results["categories"]):
            if i < len(results["precision"]):
                precision = results["precision"][i]
                recall = results["recall"][i]
                f1 = results["f1_score"][i]
                support = results["support"][i]

                report_content.append(
                    f"{category:<20} {precision:<10.3f} {recall:<10.3f} {f1:<10.3f} {support:<10d}"
                )

        report_content.append("")

        # Category distribution analysis
        true_counts = Counter(results["true_labels"])
        pred_counts = Counter(results["predicted_labels"])

        report_content.append("CATEGORY DISTRIBUTION")
        report_content.append("-" * 30)
        report_content.append(
            f"{'Category':<20} {'True':<10} {'Predicted':<10} {'Difference':<10}"
        )
        report_content.append("-" * 60)

        all_categories = set(true_counts.keys()) | set(pred_counts.keys())
        for category in sorted(all_categories):
            true_count = true_counts.get(category, 0)
            pred_count = pred_counts.get(category, 0)
            diff = pred_count - true_count

            report_content.append(
                f"{category:<20} {true_count:<10d} {pred_count:<10d} {diff:+d}"
            )

        report_content.append("")

        # Confidence analysis
        report_content.append("CONFIDENCE ANALYSIS")
        report_content.append("-" * 25)
        report_content.append(f"Min Confidence: {min(results['confidences']):.3f}")
        report_content.append(f"Max Confidence: {max(results['confidences']):.3f}")
        report_content.append(
            f"Median Confidence: {np.median(results['confidences']):.3f}"
        )
        report_content.append(f"Std Confidence: {np.std(results['confidences']):.3f}")

        # Low confidence predictions
        low_conf_threshold = 0.3
        low_conf_count = sum(
            1 for c in results["confidences"] if c < low_conf_threshold
        )
        report_content.append(
            f"Low confidence predictions (<{low_conf_threshold}): {low_conf_count}"
        )

        report_content.append("")

        # Sample predictions
        report_content.append("SAMPLE PREDICTIONS")
        report_content.append("-" * 25)

        # Show a few correct and incorrect predictions
        correct_samples = []
        incorrect_samples = []

        for i, (true_label, pred_label, confidence, prediction) in enumerate(
            zip(
                results["true_labels"],
                results["predicted_labels"],
                results["confidences"],
                results["predictions"],
            )
        ):
            sample_data = {
                "index": i,
                "true": true_label,
                "predicted": pred_label,
                "confidence": confidence,
                "subject": results["test_data"].iloc[i]["subject"] or "No subject",
                "folder": results["test_data"].iloc[i]["folder_name"],
            }

            if true_label == pred_label:
                correct_samples.append(sample_data)
            else:
                incorrect_samples.append(sample_data)

        report_content.append("CORRECT PREDICTIONS (sample):")
        for sample in correct_samples[:3]:
            report_content.append(f"  Subject: {sample['subject'][:60]}...")
            report_content.append(
                f"  Folder: {sample['folder']} -> Category: {sample['true']}"
            )
            report_content.append(f"  Confidence: {sample['confidence']:.3f}")
            report_content.append("")

        report_content.append("INCORRECT PREDICTIONS (sample):")
        for sample in incorrect_samples[:3]:
            report_content.append(f"  Subject: {sample['subject'][:60]}...")
            report_content.append(f"  Folder: {sample['folder']}")
            report_content.append(
                f"  True: {sample['true']} | Predicted: {sample['predicted']}"
            )
            report_content.append(f"  Confidence: {sample['confidence']:.3f}")
            report_content.append("")

        # Save report
        report_path = self.results_dir / "performance_report.txt"
        with open(report_path, "w") as f:
            f.write("\n".join(report_content))

        print(f"  Performance report saved to {report_path}")

        # Also save as CSV for further analysis
        results_df = pd.DataFrame(
            {
                "true_category": results["true_labels"],
                "predicted_category": results["predicted_labels"],
                "confidence": results["confidences"],
                "correct": [
                    t == p
                    for t, p in zip(results["true_labels"], results["predicted_labels"])
                ],
                "subject": results["test_data"]["subject"].values,
                "folder_name": results["test_data"]["folder_name"].values,
            }
        )

        csv_path = self.results_dir / "detailed_results.csv"
        results_df.to_csv(csv_path, index=False)
        print(f"  Detailed results saved to {csv_path}")

    def run_comprehensive_test(
        self, max_training_emails: int = 5000, num_test_samples: int = 200
    ):
        """Run the complete test suite"""
        print("🧪 STARTING COMPREHENSIVE ENRON EMAIL CLASSIFIER TEST")
        print("=" * 60)

        # Step 1: Check database
        if not self.check_database():
            print("❌ Database check failed. Exiting.")
            return False

        # Step 2: Analyze database content
        db_analysis = self.analyze_database_content()

        # Step 3: Initialize classifier
        if not self.test_classifier_initialization():
            print("❌ Classifier initialization failed. Exiting.")
            return False

        # Step 4: Train model
        if not self.test_training(max_emails=max_training_emails):
            print("❌ Training failed. Exiting.")
            return False

        # Step 5: Test predictions
        prediction_results = self.test_predictions(num_samples=num_test_samples)
        if not prediction_results:
            print("❌ Prediction testing failed. Exiting.")
            return False

        # Step 6: Generate visualizations and reports
        self.generate_confusion_matrix(prediction_results)
        self.generate_performance_report(prediction_results)

        # Step 7: Print final summary
        print("\n" + "=" * 60)
        print("🎉 TEST SUITE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"✅ Training Time: {self.training_time:.2f}s")
        print(f"✅ Overall Accuracy: {prediction_results['accuracy']:.3f}")
        print(f"✅ Balanced Accuracy: {prediction_results['balanced_accuracy']:.3f}")
        print(f"✅ Average Confidence: {prediction_results['avg_confidence']:.3f}")
        print(
            f"✅ Prediction Speed: {prediction_results['predictions_per_second']:.1f} emails/sec"
        )
        print(f"📁 Results saved to: {self.results_dir}")

        return True


def main():
    """Main function to run the test suite"""
    # Configuration
    DB_PATH = "../SQLite_db/enron.db"
    MAX_TRAINING_EMAILS = 3000  # Reduce for faster testing
    NUM_TEST_SAMPLES = 150  # Number of emails to test predictions on

    # Create and run tester
    tester = EnronClassifierTester(db_path=DB_PATH)

    try:
        success = tester.run_comprehensive_test(
            max_training_emails=MAX_TRAINING_EMAILS, num_test_samples=NUM_TEST_SAMPLES
        )

        if success:
            print("\n🎯 Test completed successfully!")
            print("Check the 'test_results' directory for detailed analysis.")
        else:
            print("\n❌ Test failed. Check the output above for details.")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
