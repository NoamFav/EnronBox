import sqlite3
import os

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
