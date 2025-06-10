import os
import sqlite3
from email import message_from_file
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
from datetime import datetime
import re

MAILDIR_PATH = "maildir"
DB_PATH = "apps/SQLite_db/enron.db"

# Thread-local storage for database connections
thread_local = threading.local()


def get_db_connection():
    """Get a thread-local database connection"""
    if not hasattr(thread_local, "conn"):
        thread_local.conn = sqlite3.connect(DB_PATH)
        thread_local.conn.execute("PRAGMA synchronous = OFF")
        thread_local.conn.execute("PRAGMA journal_mode = MEMORY")
        thread_local.conn.execute("PRAGMA cache_size = 10000")
    return thread_local.conn


def calculate_email_age_days(date_str):
    """Calculate how many days old an email is based on its date"""
    if not date_str:
        return random.randint(30, 365)  # Default to random age if no date

    try:
        # Parse common email date formats
        date_formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S",
            "%d %b %Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        email_date = None
        for fmt in date_formats:
            try:
                # Remove timezone info for simpler parsing
                clean_date = re.sub(r"\s*\([^)]+\)$", "", date_str.strip())
                clean_date = re.sub(r"\s*[+-]\d{4}$", "", clean_date)
                email_date = datetime.strptime(clean_date, fmt)
                break
            except ValueError:
                continue

        if email_date:
            # Calculate days since email was sent (assuming current date is around 2002-2004 for Enron data)
            reference_date = datetime(
                2002, 6, 1
            )  # Approximate middle of Enron email timeframe
            age_days = (reference_date - email_date).days
            return max(0, age_days)  # Ensure non-negative
        else:
            return random.randint(30, 365)
    except:
        return random.randint(30, 365)


def generate_natural_status(subject, from_addr, to_addr, date_str, folder):
    """Generate natural-looking status flags based on email characteristics"""
    age_days = calculate_email_age_days(date_str)

    # Base probabilities
    read_prob = 0.75
    starred_prob = 0.08
    flagged_prob = 0.05

    # Adjust based on email age (older emails more likely to be read)
    if age_days > 180:
        read_prob = 0.95
    elif age_days > 90:
        read_prob = 0.85
    elif age_days > 30:
        read_prob = 0.75
    else:
        read_prob = 0.60

    # Adjust based on folder type
    folder_lower = folder.lower()
    if folder_lower in ["inbox", "sent", "sent_mail"]:
        read_prob *= 1.1
    elif folder_lower in ["spam", "junk", "deleted_items"]:
        read_prob *= 0.3
        starred_prob *= 0.1
        flagged_prob *= 0.1
    elif folder_lower in ["important", "priority"]:
        starred_prob *= 3.0
        flagged_prob *= 2.0

    # Adjust based on subject indicators
    subject_lower = (subject or "").lower()
    if any(
        word in subject_lower
        for word in ["urgent", "important", "asap", "critical", "priority"]
    ):
        starred_prob *= 2.5
        flagged_prob *= 2.0
        read_prob *= 1.2
    elif any(word in subject_lower for word in ["fwd:", "fw:", "re:", "reply"]):
        read_prob *= 1.1
    elif any(word in subject_lower for word in ["meeting", "schedule", "appointment"]):
        starred_prob *= 1.5
        flagged_prob *= 1.8
    elif any(
        word in subject_lower
        for word in ["newsletter", "notification", "alert", "update"]
    ):
        read_prob *= 0.8
        starred_prob *= 0.5

    # Adjust based on sender (internal vs external)
    if from_addr and "@enron.com" in from_addr.lower():
        read_prob *= 1.15
        starred_prob *= 1.2

    # Add some natural correlation (starred emails are more likely to be read)
    is_starred = random.random() < min(starred_prob, 0.25)
    is_flagged = random.random() < min(flagged_prob, 0.20)

    # If starred or flagged, increase read probability
    if is_starred or is_flagged:
        read_prob *= 1.4

    is_read = random.random() < min(read_prob, 0.98)

    return {
        "read": 1 if is_read else 0,
        "starred": 1 if is_starred else 0,
        "flagged": 1 if is_flagged else 0,
        "deleted": 0,  # We'll assume these are active emails
        "archived": 0,
    }


def parse_email_batch(file_paths):
    """Parse multiple emails in a batch"""
    results = []
    for file_path in file_paths:
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

                # Extract path components
                rel_parts = os.path.relpath(file_path, MAILDIR_PATH).split(os.sep)
                if len(rel_parts) >= 3:
                    username = rel_parts[0]
                    folder = rel_parts[1]
                    filename = rel_parts[2]

                    # Generate natural status flags
                    status = generate_natural_status(
                        subject, from_addr, to_addr, date, folder
                    )

                    results.append(
                        (
                            username,
                            folder,
                            filename,
                            from_addr,
                            to_addr,
                            subject,
                            date,
                            body,
                            status,
                        )
                    )
        except Exception as e:
            print(f"❌ Failed to parse {file_path}: {e}")
    return results


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
            read INTEGER DEFAULT 0,
            starred INTEGER DEFAULT 0,
            flagged INTEGER DEFAULT 0,
            important INTEGER DEFAULT 0,
            deleted INTEGER DEFAULT 0,
            archived INTEGER DEFAULT 0,
            FOREIGN KEY(folder_id) REFERENCES folders(id)
        );
    """
    )
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

    # Add columns for email status if they don't exist
    cursor.execute("PRAGMA table_info(emails);")
    columns = [row[1] for row in cursor.fetchall()]
    new_fields = [
        ("starred", "INTEGER DEFAULT 0"),
        ("flagged", "INTEGER DEFAULT 0"),
        ("deleted", "INTEGER DEFAULT 0"),
        ("archived", "INTEGER DEFAULT 0"),
        ("read", "INTEGER DEFAULT 0"),
    ]
    for col, col_type in new_fields:
        if col not in columns:
            cursor.execute(f"ALTER TABLE emails ADD COLUMN {col} {col_type};")


def collect_all_files():
    """Collect all email file paths upfront"""
    file_paths = []
    for root, dirs, files in os.walk(MAILDIR_PATH):
        for file in files:
            path = os.path.join(root, file)
            rel_parts = os.path.relpath(path, MAILDIR_PATH).split(os.sep)
            if len(rel_parts) >= 3:  # username/folder/filename
                file_paths.append(path)
    return file_paths


def batch_insert_data(parsed_emails):
    """Insert data in batches with optimized lookups"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Optimize SQLite settings for bulk inserts
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA cache_size = 10000")
    cursor.execute("BEGIN TRANSACTION")

    try:
        # Pre-load existing users and folders
        cursor.execute("SELECT username, id FROM users")
        user_cache = dict(cursor.fetchall())

        cursor.execute("SELECT user_id, name, id FROM folders")
        folder_cache = {}
        for user_id, name, folder_id in cursor.fetchall():
            folder_cache[(user_id, name)] = folder_id

        # Collect unique users and folders
        unique_users = set()
        unique_folders = set()
        for username, folder, _, _, _, _, _, _, _ in parsed_emails:
            unique_users.add(username)
            unique_folders.add((username, folder))

        # Batch insert new users
        new_users = [(u,) for u in unique_users if u not in user_cache]
        if new_users:
            cursor.executemany(
                "INSERT OR IGNORE INTO users (username) VALUES (?)", new_users
            )
            # Refresh user cache
            cursor.execute("SELECT username, id FROM users")
            user_cache = dict(cursor.fetchall())

        # Batch insert new folders
        new_folders = []
        for username, folder in unique_folders:
            user_id = user_cache[username]
            if (user_id, folder) not in folder_cache:
                new_folders.append((user_id, folder))

        if new_folders:
            cursor.executemany(
                "INSERT OR IGNORE INTO folders (user_id, name) VALUES (?, ?)",
                new_folders,
            )
            # Refresh folder cache
            cursor.execute("SELECT user_id, name, id FROM folders")
            folder_cache = {}
            for user_id, name, folder_id in cursor.fetchall():
                folder_cache[(user_id, name)] = folder_id

        # Batch insert emails with natural status flags
        email_data = []
        status_stats = {"read": 0, "starred": 0, "flagged": 0}

        for (
            username,
            folder,
            filename,
            from_addr,
            to_addr,
            subject,
            date,
            body,
            status,
        ) in parsed_emails:
            user_id = user_cache[username]
            folder_id = folder_cache[(user_id, folder)]

            email_data.append(
                (
                    folder_id,
                    filename,
                    subject,
                    body,
                    from_addr,
                    to_addr,
                    date,
                    status["read"],
                    status["starred"],
                    status["flagged"],
                    status.get("important", 0),
                    status["deleted"],
                    status["archived"],
                )
            )

            # Track statistics
            if status["read"]:
                status_stats["read"] += 1
            if status["starred"]:
                status_stats["starred"] += 1
            if status["flagged"]:
                status_stats["flagged"] += 1

        cursor.executemany(
            """INSERT INTO emails (folder_id, filename, subject, body, from_address, to_address, date, read, starred, flagged, important, deleted, archived)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            email_data,
        )

        cursor.execute("COMMIT")
        print(f"✅ Inserted {len(email_data)} emails")
        print(f"📊 Status distribution:")
        print(
            f"   📖 Read: {status_stats['read']} ({status_stats['read']/len(email_data)*100:.1f}%)"
        )
        print(
            f"   ⭐ Starred: {status_stats['starred']} ({status_stats['starred']/len(email_data)*100:.1f}%)"
        )
        print(
            f"   🚩 Flagged: {status_stats['flagged']} ({status_stats['flagged']/len(email_data)*100:.1f}%)"
        )

    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"❌ Error during batch insert: {e}")
        raise
    finally:
        conn.close()


def main():
    if not os.path.exists(MAILDIR_PATH):
        print(f"❌ Maildir not found at '{MAILDIR_PATH}'")
        return

    # Initialize database schema
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    init_schema(cursor)
    conn.commit()
    conn.close()

    # Collect all file paths
    print("📁 Collecting file paths...")
    file_paths = collect_all_files()
    print(f"📧 Found {len(file_paths)} email files")

    # Process emails in parallel batches
    batch_size = 100
    max_workers = min(8, os.cpu_count() or 4)

    print(f"🚀 Processing with {max_workers} workers in batches of {batch_size}")
    print("🎲 Generating natural email status flags...")

    all_parsed_emails = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit batches for parallel processing
        futures = []
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i : i + batch_size]
            future = executor.submit(parse_email_batch, batch)
            futures.append(future)

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                batch_results = future.result()
                all_parsed_emails.extend(batch_results)
            except Exception as e:
                print(f"❌ Batch processing error: {e}")

    # Insert all data in one optimized batch
    print("💾 Inserting into database...")
    batch_insert_data(all_parsed_emails)

    print(f"✅ Successfully created {DB_PATH} from {MAILDIR_PATH}")
    print(f"📊 Total emails processed: {len(all_parsed_emails)}")


if __name__ == "__main__":
    main()
