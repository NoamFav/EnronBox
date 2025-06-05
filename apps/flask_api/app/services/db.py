import sqlite3
import os
import json
import random
from typing import List, Dict, Any

print("DB_PATH:", os.getenv("DB_PATH"))
DB_PATH = os.getenv("DB_PATH", "apps/SQLite_db/enron.db")


def get_db_connection():
    try:
        print(f"Attempting to connect to database at: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        ensure_email_schema(conn)  # Ensure new columns are initialized to avoid 500 errors
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {str(e)}")
        raise


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

def ensure_email_schema(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(emails);")
    existing_columns = [row[1] for row in cursor.fetchall()]

    new_fields = [
        ("starred", "INTEGER DEFAULT 0"),
        ("flagged", "INTEGER DEFAULT 0"),
        ("deleted", "INTEGER DEFAULT 0"),
        ("archived", "INTEGER DEFAULT 0"),
        ("read", "INTEGER DEFAULT 0"),
    ]

    new_column_added = False

    for col, col_type in new_fields:
        if col not in existing_columns:
            print(f"Adding missing column: {col}")
            cursor.execute(f"ALTER TABLE emails ADD COLUMN {col} {col_type};")
            new_column_added = True

    conn.commit()

    if new_column_added:
        print("Initializing random flags for newly added columns...")
        conn.commit()  # Commit schema change first
        initialize_column_values_once(conn)
    else:
        conn.commit()

def initialize_column_values_once(conn):
    """Randomize initial values for the first 500 emails only."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM emails ORDER BY id ASC LIMIT 500;")
    email_ids = [row[0] for row in cursor.fetchall()]
    total = len(email_ids)

    def set_random_flags(col_name, ratio):
        sample_size = int(ratio * total)
        selected_ids = random.sample(email_ids, sample_size)

        cursor.executemany(
            f"UPDATE emails SET {col_name} = 1 WHERE id = ?",
            [(eid,) for eid in selected_ids]
        )
        conn.commit()

    print(f"Initializing flags for first {total} emails...")
    set_random_flags("read", 0.3)
    set_random_flags("flagged", 0.2)
    set_random_flags("starred", 0.3)

    print("Initialization complete.")


def get_emails(username, folder_name):
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT emails.id, emails.subject, emails.body, emails.from_address, emails.to_address, emails.date,
               emails.starred, emails.flagged, emails.deleted, emails.archived, emails.read
        FROM emails
        JOIN folders ON emails.folder_id = folders.id
        JOIN users ON folders.user_id = users.id
        WHERE users.username = ? AND folders.name = ? AND emails.deleted = 0
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
               emails.starred, emails.flagged, emails.deleted, emails.archived, emails.read,
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

        # Table for storing emails
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER,
                filename TEXT,
                subject TEXT,
                body TEXT,
                from_address TEXT,
                to_address TEXT,
                date TEXT,
                read INTEGER DEFAULT 0,
                starred INTEGER DEFAULT 0,
                important INTEGER DEFAULT 0,
                deleted INTEGER DEFAULT 0,
                FOREIGN KEY(folder_id) REFERENCES folders(id)
            );
        """
        )
        conn.commit()


def store_data(table: str, data: List[Dict[str, Any]]):
    """
    Generic function to store data into a specified table. Remember to initialize the table in initialize_table function.

    Args:
        table (str): The name of the table to store data into.
        data (List[Dict[str, Any]]): A list of dictionaries containing the data to store.
    """

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


def update_email_flags(email_id: int, read: bool = None, starred: bool = None, important: bool = None, deleted: bool = None):
    """
    Update email flags (read, starred, important, deleted) in the database.
    Only updates the fields that are not None.
    """
    fields = []
    values = []
    if read is not None:
        fields.append("read = ?")
        values.append(int(read))
    if starred is not None:
        fields.append("starred = ?")
        values.append(int(starred))
    if important is not None:
        fields.append("important = ?")
        values.append(int(important))
    if deleted is not None:
        fields.append("deleted = ?")
        values.append(int(deleted))
    if not fields:
        return
    values.append(email_id)
    sql = f"UPDATE emails SET {', '.join(fields)} WHERE id = ?"
    with get_db_connection() as conn:
        conn.execute(sql, values)
        conn.commit()


def get_email_flags(email_id: int):
    """
    Get the flags (read, starred, important, deleted) for a given email.
    """
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT read, starred, important, deleted FROM emails WHERE id = ?", (email_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "read": bool(row["read"]),
                "starred": bool(row["starred"]),
                "important": bool(row["important"]),
                "deleted": bool(row["deleted"]),
            }
        return None

def store_email_status(email_id: str, status_update: Dict[str, int]):
    """
    Store email status updates in the database.
    
    Args:
        email_id (str): email ID
        status_update (Dict[str, int]): status such as {'starred': 1} or {'flagged': 0}
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for field, value in status_update.items():
                cursor.execute(
                    f"UPDATE emails SET {field} = ? WHERE id = ?",
                    (value, email_id)
                )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error updating email status: {str(e)}")
        return False
