#!/usr/bin/env python3
"""
Script to test the Enron dataset before training
"""

import sys
import sqlite3
from pathlib import Path


def test_enron_database(db_path: str, max_emails: int = 1000):
    """Test the Enron database structure and content"""

    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ["emails", "folders"]
        missing_tables = [table for table in required_tables if table not in tables]

        if missing_tables:
            print(f"❌ Missing required tables: {missing_tables}")
            return False

        print(f"✅ Database structure looks good")
        print(f"   Tables found: {tables}")

        # Check email count
        cursor.execute("SELECT COUNT(*) FROM emails")
        total_emails = cursor.fetchone()[0]
        print(f"   Total emails in database: {total_emails:,}")

        # Check folder distribution
        query = """
            SELECT f.name, COUNT(e.id) as email_count
            FROM folders f
            LEFT JOIN emails e ON f.id = e.folder_id
            GROUP BY f.id, f.name
            ORDER BY email_count DESC
        """
        cursor.execute(query)
        folder_counts = cursor.fetchall()

        print(f"\n📁 Folder distribution:")
        for folder_name, count in folder_counts[:10]:  # Show top 10
            print(f"   {folder_name}: {count:,} emails")

        if len(folder_counts) > 10:
            print(f"   ... and {len(folder_counts) - 10} more folders")

        # Sample some emails to check content quality
        query = """
            SELECT e.subject, e.body, f.name as folder_name
            FROM emails e
            JOIN folders f ON e.folder_id = f.id
            WHERE e.subject IS NOT NULL AND e.body IS NOT NULL
            LIMIT 5
        """
        cursor.execute(query)
        sample_emails = cursor.fetchall()

        print(f"\n📧 Sample emails:")
        for i, (subject, body, folder) in enumerate(sample_emails, 1):
            subject_preview = subject[:50] + "..." if len(subject) > 50 else subject
            body_preview = body[:100] + "..." if len(body) > 100 else body
            print(f"   {i}. [{folder}] {subject_preview}")
            print(f"      {body_preview.replace(chr(10), ' ')}")
            print()

        conn.close()

        if total_emails < 10:
            print(
                f"⚠️  Warning: Very few emails ({total_emails}). Training may not work well."
            )
            return False

        return True

    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_dataset.py <path_to_enron.db>")
        sys.exit(1)

    db_path = sys.argv[1]
    print(f"Testing Enron database: {db_path}")
    print("=" * 60)

    success = test_enron_database(db_path)

    print("=" * 60)
    if success:
        print("✅ Database test passed! You can proceed with training.")
        print("\nTo analyze the dataset before training, use:")
        print(
            'curl -X POST http://localhost:5050/api/classify/train -H "Content-Type: application/json" -d \'{"enron_dir": "'
            + db_path
            + '", "analyze_only": true}\''
        )
    else:
        print("❌ Database test failed. Please check the database file.")


if __name__ == "__main__":
    main()
