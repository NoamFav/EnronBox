#!/usr/bin/env python3
"""
app/tests/eval_classification.py

Evaluate and compare a traditional TF–IDF + SGDClassifier baseline
against the transformer–fine-tuned EnronEmailClassifier on your Enron dataset.
"""
import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from app.services.enron_classifier import EnronEmailClassifier


class ClassificationEvaluator:
    def __init__(
        self,
        db_path: str,
        model_dir: str,
        test_size: float = 0.2,
        random_state: int = 42,
        sample_per_class: int = 400,
    ):
        self.db_path = Path(db_path)
        self.model_dir = Path(model_dir)
        self.test_size = test_size
        self.random_state = random_state
        self.sample_per_class = sample_per_class

        # load categories from your classifier
        tmp = EnronEmailClassifier(model_dir=str(self.model_dir))
        self.categories = tmp.categories

    def _folder_to_idx(self, folder_name: str) -> int:
        """Map a folder name to one of the classifier's category indices."""
        low = folder_name.lower()
        for idx, cat in enumerate(self.categories):
            if cat.lower() in low:
                return idx
        return 0  # fallback to first category

    def load_and_prepare(self):
        conn = sqlite3.connect(str(self.db_path))
        dfs = []
        for cat in self.categories:
            df_cat = pd.read_sql_query(
                """
                SELECT
                  e.subject || ' ' || e.body AS text,
                  f.name               AS folder
                FROM emails e
                JOIN folders f ON e.folder_id = f.id
                WHERE LOWER(f.name) LIKE ?
                LIMIT ?
                """,
                conn,
                params=[f"%{cat.lower()}%", self.sample_per_class],
            )
            dfs.append(df_cat)
        conn.close()

        df = pd.concat(dfs, ignore_index=True)
        df = df[df["text"].str.strip().astype(bool)]
        print(f"Loaded {len(df)} non-blank emails (balanced per class)")

        df["label"] = df["folder"].map(self._folder_to_idx)
        self.X = df["text"].values
        self.y = df["label"].values

    def split(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X,
            self.y,
            test_size=self.test_size,
            stratify=self.y,
            random_state=self.random_state,
        )
        print(
            f"Split into {len(self.X_train)} train and {len(self.X_test)} test samples"
        )

    def eval_baseline(self):
        vect = TfidfVectorizer(ngram_range=(1, 2), max_features=10_000)
        Xtr_tfidf = vect.fit_transform(self.X_train)
        clf_base = SGDClassifier(
            loss="log_loss",
            max_iter=1000,
            random_state=self.random_state,
            class_weight="balanced",
        )
        clf_base.fit(Xtr_tfidf, self.y_train)
        y_pred = clf_base.predict(vect.transform(self.X_test))

        labels_present = sorted(set(self.y_test))
        names_present = [self.categories[i] for i in labels_present]
        print("\n=== TF–IDF + SGDClassifier ===")
        print(
            classification_report(
                self.y_test,
                y_pred,
                labels=labels_present,
                target_names=names_present,
            )
        )

    def eval_transformer(self):
        # 1) Load classifier (it will load pickles if present, or leave uninitialized)
        clf = EnronEmailClassifier(model_dir=str(self.model_dir))

        # 2) Build a DataFrame in the format train() expects
        import pandas as pd

        train_df = pd.DataFrame(
            {
                "subject": ["" for _ in self.X_train],
                "body": self.X_train,
                "sender": ["" for _ in self.X_train],
                "has_attachment": [False for _ in self.X_train],
                "num_recipients": [1 for _ in self.X_train],
                "time_sent": pd.to_datetime("2025-01-01"),
            }
        )

        # 3) Fine-tune the transformer on your train split
        print("\nFine-tuning transformer on train split...")
        clf.train(train_df, self.y_train)

        # 4) Now evaluate on the held-out test split
        y_pred = clf.text_model.predict(self.X_test)

    def run(self):
        print(f"Preparing data from {self.db_path}")
        self.load_and_prepare()
        self.split()
        self.eval_baseline()
        self.eval_transformer()


if __name__ == "__main__":
    # adjust paths as needed
    ROOT = Path(__file__).resolve().parents[2]
    DB_PATH = "../SQLite_db/enron.db"
    MODEL_DIR = ROOT / "models"

    evaluator = ClassificationEvaluator(
        db_path=str(DB_PATH),
        model_dir=str(MODEL_DIR),
        test_size=0.2,
        sample_per_class=600,
    )
    evaluator.run()
