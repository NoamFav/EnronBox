import sqlite3
import os
import json
from typing import List, Dict, Any

print("DB_PATH:", os.getenv("DB_PATH"))
DB_PATH = os.getenv("DB_PATH", "/app/data/enron.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_users():
    conn = get_db_connection()
    cursor = conn.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def get_folders_for_user(username):
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT folders.id, folders.name
        FROM folders
        JOIN users ON folders.user_id = users.id
        WHERE users.username = ?
        """,
        (username,),
    )
    folders = cursor.fetchall()
    conn.close()
    return folders


def get_emails(username, folder_name):
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT emails.id, emails.subject, emails.body, emails.from_address, emails.to_address, emails.date
        FROM emails
        JOIN folders ON emails.folder_id = folders.id
        JOIN users ON folders.user_id = users.id
        WHERE users.username = ? AND folders.name = ?
        ORDER BY emails.date DESC
        LIMIT 100
        """,
        (username, folder_name),
    )
    emails = cursor.fetchall()
    conn.close()
    return emails


def get_email_by_id(email_id):
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT emails.id, emails.subject, emails.body, emails.from_address, emails.to_address, emails.date,
               folders.name as folder_name, users.username
        FROM emails
        JOIN folders ON emails.folder_id = folders.id
        JOIN users ON folders.user_id = users.id
        WHERE emails.id = ?
        """,
        (email_id,),
    )
    email = cursor.fetchone()
    conn.close()
    return email


def initialize_table():
    """Initialize required tables in the DB if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Table for storing serialized model predictions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence REAL NOT NULL,
                polarity REAL NOT NULL,
                subjectivity REAL NOT NULL,
                stress_score REAL NOT NULL,
                relaxation_score REAL NOT NULL
            )
        """
        )

        # Table for storing and indexing entities
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL
            )
        """
        )
        conn.commit()


def store_data(table: str, data: List[Dict[str, Any]]):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if table == "predictions":
            cursor.executemany(
                """
                INSERT INTO predictions (email_id, category, confidence, polarity, subjectivity, stress_score, relaxation_score)
                VALUES (:email_id, :category, :confidence, :polarity, :subjectivity, :stress_score, :relaxation_score)
            """,
                data,
            )
        elif table == "entities":
            cursor.executemany(
                """
                INSERT INTO entities (email_id, entity_type, entity_value)
                VALUES (:email_id, :entity_type, :entity_value)
            """,
                data,
            )
        elif table == "email_classifications":
            cursor.executemany(
                """
                INSERT INTO email_classifications (
                    email_id,
                    category,
                    category_name,
                    confidence,
                    transformer_category,
                    transformer_confidence,
                    polarity,
                    subjectivity,
                    stress_score,
                    relaxation_score
                )
                VALUES (
                    :email_id,
                    :category,
                    :category_name,
                    :confidence,
                    :transformer_category,
                    :transformer_confidence,
                    :polarity,
                    :subjectivity,
                    :stress_score,
                    :relaxation_score
                )
            """,
                data,
            )
        else:
            raise ValueError(f"Unknown table: {table}")

        conn.commit()


def store_prediction(self, email_id: str, prediction: Dict[str, Any]):
    """
    Save model prediction results to the database.

    Args:
        email_id (str): The ID of the email.
        prediction (Dict[str, Any]): The prediction result from the model.
    """
    from app.services.enron_classifier import EnronEmailClassifier

    serialized_prediction = EnronEmailClassifier.serialize_prediction(
        email_id, prediction
    )
    store_data("predictions", [serialized_prediction])


def store_entities(email_id: str, entities: Dict[str, List[str]]):
    """
    Store and index entities into the database.

    Args:
        email_id (str): The ID of the email.
        entities (Dict[str, List[str]]): A dictionary of entities with their types and values.
    """
    entity_data = []

    for entity_type, values in entities.items():
        for value in values:
            entity_data.append(
                {
                    "email_id": email_id,
                    "entity_type": entity_type,
                    "entity_value": value,
                }
            )

    store_data("entities", entity_data)
