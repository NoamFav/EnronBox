import sqlite3
import os


DB_PATH = os.getenv("DB_PATH", "/app/data/enron.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_users():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users").fetchall()


def get_folders_for_user(username):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT f.name FROM folders f
            JOIN users u ON f.user_id = u.id
            WHERE u.username = ?
        """,
            (username,),
        ).fetchall()


def get_emails(username, folder):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT e.id, e.subject, e.date
            FROM emails e
            JOIN folders f ON e.folder_id = f.id
            JOIN users u ON f.user_id = u.id
            WHERE u.username = ? AND f.name = ?
            ORDER BY e.date DESC
            LIMIT 50
        """,
            (username, folder),
        ).fetchall()


def get_email_by_id(email_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
