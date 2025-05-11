import sqlite3
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from clean_body import clean_body
from tokenize_body import normalize_text
from vectorize import vectorize_texts
from anonymization import anonymize_text

def process_email(email_body):

    cleaned = clean_body(email_body)
    anonymized = anonymize_text(cleaned)
    tokens = normalize_text(anonymized)

    return ' '.join(tokens)

def load_emails_from_database(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT body FROM emails")
    emails = [row[0] for row in cursor.fetchall()]

    connection.close()
    return emails

def multithread_loading(db_path):
    email_bodies = load_emails_from_database(db_path)

    with ThreadPoolExecutor() as thread_executor:
        future_to_body = {thread_executor.submit(process_email, body): body for body in email_bodies}
        processed_texts = []
        
        for future in as_completed(future_to_body):
            try:
                processed_text = future.result()
                processed_texts.append(processed_text)
            except Exception as e:
                print(f"Error when processing: {e}")

    with ProcessPoolExecutor() as process_executor:
        future = process_executor.submit(vectorize_texts, processed_texts)
        vectorized_output = future.result()

    return processed_texts, vectorized_output

if __name__ == "__main__":
    database_directory = 'apps/SQLite_db/enron.db'
    tokens_list, vectors = multithread_loading(database_directory)
    print("Tokenized Emails:", tokens_list)
    print("Vectorized Output:", vectors.toarray())
