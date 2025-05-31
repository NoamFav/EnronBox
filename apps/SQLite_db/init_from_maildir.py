import os
import sqlite3
from email import message_from_file

MAILDIR_PATH = "maildir"
DB_PATH = "enron.db"


def parse_email(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            msg = message_from_file(f)
            from_addr = msg.get("From", "")
            to_addr = msg.get("To", "")
            subject = msg.get("Subject", "")
            date = msg.get("Date", "")
            body = msg.get_payload()
            if isinstance(body, list):
                body = "\n".join(
                    str(part.get_payload(decode=True) or part.get_payload())
                    for part in body
                )
            return from_addr, to_addr, subject, date, body
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
        return "", "", "", "", ""


def init_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            UNIQUE(user_id, name),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """
    )
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
            FOREIGN KEY(folder_id) REFERENCES folders(id)
        );
    """
    )
    # Add the email_classifications table for storing ML predictions
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS email_classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT NOT NULL,
            category TEXT NOT NULL,
            category_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            transformer_category TEXT,
            transformer_confidence REAL,
            polarity REAL,
            subjectivity REAL,
            stress_score REAL,
            relaxation_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(email_id) ON CONFLICT REPLACE
        );
    """
    )


def get_user_id(cursor, username):
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
    return cursor.lastrowid


def get_folder_id(cursor, user_id, folder_name):
    cursor.execute(
        "SELECT id FROM folders WHERE user_id = ? AND name = ?", (user_id, folder_name)
    )
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(
        "INSERT INTO folders (user_id, name) VALUES (?, ?)", (user_id, folder_name)
    )
    return cursor.lastrowid


def populate_db(cursor):
    for root, dirs, files in os.walk(MAILDIR_PATH):
        for file in files:
            path = os.path.join(root, file)
            rel_parts = os.path.relpath(path, MAILDIR_PATH).split(os.sep)
            if len(rel_parts) < 3:
                continue
            username = rel_parts[0]
            folder = rel_parts[1]
            filename = rel_parts[2]
            from_addr, to_addr, subject, date, body = parse_email(path)
            user_id = get_user_id(cursor, username)
            folder_id = get_folder_id(cursor, user_id, folder)
            cursor.execute(
                """
                INSERT INTO emails (folder_id, filename, subject, body, from_address, to_address, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (folder_id, filename, subject, body, from_addr, to_addr, date),
            )


def main():
    if not os.path.exists(MAILDIR_PATH):
        print(f"❌ Maildir not found at '{MAILDIR_PATH}'")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    init_schema(cursor)
    populate_db(cursor)
    conn.commit()
    conn.close()
    print(f"✅ Successfully created nested {DB_PATH} from {MAILDIR_PATH}")


if __name__ == "__main__":
    main()
