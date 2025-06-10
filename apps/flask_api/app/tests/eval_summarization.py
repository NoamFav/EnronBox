# eval_summarization.py
from app.services.summarizer import EmailSummarizer
from app.services.db import get_db_connection
from rouge import Rouge
import json
import os
import argparse
import sqlite3
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sklearn.metrics import f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from collections import defaultdict
import sys
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("[INFO] Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')

def safe_rouge_score(generated, reference):
    """Safely calculate ROUGE scores, handling edge cases"""
    if not generated or not reference or not generated.strip() or not reference.strip():
        return {
            'rouge-1': {'r': 0.0, 'p': 0.0, 'f': 0.0},
            'rouge-2': {'r': 0.0, 'p': 0.0, 'f': 0.0},
            'rouge-l': {'r': 0.0, 'p': 0.0, 'f': 0.0}
        }

    try:
        # Clean the text to prevent recursion issues
        generated_clean = ' '.join(generated.split())
        reference_clean = ' '.join(reference.split())

        # Ensure minimum length
        if len(generated_clean) < 1 or len(reference_clean) < 1:
            return {
                'rouge-1': {'r': 0.0, 'p': 0.0, 'f': 0.0},
                'rouge-2': {'r': 0.0, 'p': 0.0, 'f': 0.0},
                'rouge-l': {'r': 0.0, 'p': 0.0, 'f': 0.0}
            }

        rouge = Rouge()
        scores = rouge.get_scores(generated_clean, reference_clean)[0]
        return scores
    except Exception as e:
        print(f"[WARNING] ROUGE calculation failed: {e}")
        return {
            'rouge-1': {'r': 0.0, 'p': 0.0, 'f': 0.0},
            'rouge-2': {'r': 0.0, 'p': 0.0, 'f': 0.0},
            'rouge-l': {'r': 0.0, 'p': 0.0, 'f': 0.0}
        }

def safe_f1_score(generated, reference):
    """Calculate F1 score using TF-IDF similarity"""
    if not generated or not reference or not generated.strip() or not reference.strip():
        return 0.0

    try:
        # Use TF-IDF to convert texts to vectors
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)

        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([generated, reference])

        # Calculate cosine similarity as proxy for F1
        similarity = np.dot(tfidf_matrix[0], tfidf_matrix[1].T).toarray()[0][0]

        # Convert similarity to F1-like score (0-1 range)
        f1 = max(0.0, min(1.0, similarity))

        return f1
    except Exception as e:
        print(f"[WARNING] F1 calculation failed: {e}")
        return 0.0

def safe_bleu_score(generated, reference):
    """Safely calculate BLEU score with smoothing"""
    if not generated or not reference or not generated.strip() or not reference.strip():
        return {'bleu-1': 0.0, 'bleu-2': 0.0, 'bleu-3': 0.0, 'bleu-4': 0.0}

    try:
        # Tokenize the sentences
        generated_tokens = nltk.word_tokenize(generated.lower())
        reference_tokens = [nltk.word_tokenize(reference.lower())]

        # Ensure minimum token length
        if len(generated_tokens) < 1 or len(reference_tokens[0]) < 1:
            return {'bleu-1': 0.0, 'bleu-2': 0.0, 'bleu-3': 0.0, 'bleu-4': 0.0}

        # Use smoothing to handle cases with no n-gram matches
        smoothie = SmoothingFunction().method4

        # Calculate BLEU score with different n-gram weights
        bleu_scores = {}
        bleu_scores['bleu-1'] = sentence_bleu(reference_tokens, generated_tokens, weights=(1, 0, 0, 0), smoothing_function=smoothie)
        bleu_scores['bleu-2'] = sentence_bleu(reference_tokens, generated_tokens, weights=(0.5, 0.5, 0, 0), smoothing_function=smoothie)
        bleu_scores['bleu-3'] = sentence_bleu(reference_tokens, generated_tokens, weights=(0.33, 0.33, 0.33, 0), smoothing_function=smoothie)
        bleu_scores['bleu-4'] = sentence_bleu(reference_tokens, generated_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothie)

        return bleu_scores
    except Exception as e:
        print(f"[WARNING] BLEU calculation failed: {e}")
        return {'bleu-1': 0.0, 'bleu-2': 0.0, 'bleu-3': 0.0, 'bleu-4': 0.0}

def extract_email_body(thread):
    """Extract only the email body from the thread, removing headers"""
    lines = thread.split('\n')

    # Find where the headers end (look for empty line after headers)
    body_start_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == '' and i > 0:
            body_start_idx = i + 1
            break
        elif not any(header in line.lower() for header in ['from:', 'to:', 'subject:', 'date:', 'cc:', 'bcc:']):
            body_start_idx = i
            break

    # Join the body lines
    body = '\n'.join(lines[body_start_idx:]).strip()
    return body if body else thread  # fallback to full thread if no body found

def get_emails_from_db(limit=5):
    """Get emails from the database for evaluation using the db service"""
    print(f"[DEBUG] Attempting to load emails from database using db service")

    try:
        # Use the get_db_connection function from db.py
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get emails from the database with better filtering
        cursor.execute("""
            SELECT id, subject, body, from_address, to_address, date
            FROM emails
            WHERE body IS NOT NULL AND body != '' AND subject IS NOT NULL AND subject != ''
            AND LENGTH(body) > 50 AND LENGTH(subject) > 5
            ORDER BY LENGTH(body) DESC
            LIMIT ?
        """, (limit,))

        emails = cursor.fetchall()
        conn.close()

        if not emails:
            print("[DEBUG] No emails found in database")
            return []

        print(f"[DEBUG] Successfully loaded {len(emails)} emails from database")

        # Format emails for evaluation
        formatted_emails = []
        for email in emails:
            # Create a simple thread format with from/to/subject/body
            thread = f"From: {email['from_address']}\nTo: {email['to_address']}\nSubject: {email['subject']}\n\n{email['body']}"

            # Extract only the email body for comparison
            email_body = extract_email_body(thread)

            # Use the email body itself as reference (first 2-3 sentences for ground truth)
            body_sentences = email_body.split('.')[:3]  # Take first 3 sentences as reference
            reference_summary = '. '.join(sentence.strip() for sentence in body_sentences if sentence.strip())

            # If reference is too short, use more sentences
            if len(reference_summary) < 50 and len(email_body.split('.')) > 3:
                body_sentences = email_body.split('.')[:5]
                reference_summary = '. '.join(sentence.strip() for sentence in body_sentences if sentence.strip())

            formatted_emails.append({
                "thread": thread,
                "email_body": email_body,  # Store body separately for comparison
                "summary": reference_summary if reference_summary else email['subject'],
                "email_id": email['id']
            })

        return formatted_emails

    except Exception as e:
        print(f"[DEBUG] Error loading emails from database: {e}")
        return []

def print_detailed_scores(rouge_scores, bleu_scores, f1_score, email_id, email_body, reference, generated):
    """Print detailed evaluation scores"""
    print(f"Email ID: {email_id}")
    print(f"Email Body: {email_body[:150]}...")
    print(f"Reference summary: {reference}")
    print(f"Generated summary: {generated}")

    # Print ROUGE scores
    print("ROUGE Scores:")
    for metric in ['rouge-1', 'rouge-2', 'rouge-l']:
        r = rouge_scores[metric]['r']
        p = rouge_scores[metric]['p']
        f = rouge_scores[metric]['f']
        print(f"  {metric.upper()}: R={r:.4f}, P={p:.4f}, F1={f:.4f}")

    # Print BLEU scores
    print("BLEU Scores:")
    for metric, score in bleu_scores.items():
        print(f"  {metric.upper()}: {score:.4f}")

    # Print F1 score
    print(f"TF-IDF F1 Score: {f1_score:.4f}")

    print("-" * 80)

def calculate_averages(all_rouge_scores, all_bleu_scores, all_f1_scores):
    """Calculate average scores across all examples"""
    if not all_rouge_scores:
        return {}, {}, 0.0

    # Calculate average ROUGE scores
    avg_rouge = {}
    for metric in ['rouge-1', 'rouge-2', 'rouge-l']:
        avg_rouge[metric] = {
            'r': sum(scores[metric]['r'] for scores in all_rouge_scores) / len(all_rouge_scores),
            'p': sum(scores[metric]['p'] for scores in all_rouge_scores) / len(all_rouge_scores),
            'f': sum(scores[metric]['f'] for scores in all_rouge_scores) / len(all_rouge_scores)
        }

    # Calculate average BLEU scores
    avg_bleu = {}
    if all_bleu_scores:
        for metric in ['bleu-1', 'bleu-2', 'bleu-3', 'bleu-4']:
            avg_bleu[metric] = sum(scores[metric] for scores in all_bleu_scores) / len(all_bleu_scores)

    # Calculate average F1 score
    avg_f1 = sum(all_f1_scores) / len(all_f1_scores) if all_f1_scores else 0.0

    return avg_rouge, avg_bleu, avg_f1

# Parse command line arguments
parser = argparse.ArgumentParser(description='Evaluate email summarization')
parser.add_argument('--use-db', action='store_true', help='Use emails from database instead of sample data')
parser.add_argument('--limit', type=int, default=5, help='Number of emails to load from database')
parser.add_argument('--verbose', action='store_true', help='Print detailed scores for each example')
args = parser.parse_args()

# Sample data (only used as fallback if database is not available)
sample_data = [
    {
        "thread": "From: John Smith\nTo: Jane Doe\nSubject: Project Update\n\nHi Jane,\n\nI wanted to update you on the project status. We've completed the first phase and are moving to phase two next week. The team has been working hard and we're on track to meet our deadline.\n\nPlease let me know if you have any questions.\n\nBest,\nJohn",
        "email_body": "Hi Jane,\n\nI wanted to update you on the project status. We've completed the first phase and are moving to phase two next week. The team has been working hard and we're on track to meet our deadline.\n\nPlease let me know if you have any questions.\n\nBest,\nJohn",
        "summary": "I wanted to update you on the project status. We've completed the first phase and are moving to phase two next week. The team has been working hard and we're on track to meet our deadline."
    },
    {
        "thread": "From: Marketing Team\nTo: All Staff\nSubject: New Product Launch\n\nDear Team,\n\nWe're excited to announce the launch of our new product next month. This represents six months of hard work and we believe it will significantly increase our market share.\n\nTraining sessions will be held next week to familiarize everyone with the product features.\n\nRegards,\nMarketing Team",
        "email_body": "Dear Team,\n\nWe're excited to announce the launch of our new product next month. This represents six months of hard work and we believe it will significantly increase our market share.\n\nTraining sessions will be held next week to familiarize everyone with the product features.\n\nRegards,\nMarketing Team",
        "summary": "We're excited to announce the launch of our new product next month. This represents six months of hard work and we believe it will significantly increase our market share. Training sessions will be held next week to familiarize everyone with the product features."
    }
]

# Decide which data source to use
if args.use_db:
    print("[DEBUG] Using database as data source")
    examples = get_emails_from_db(args.limit)

    if not examples:
        print("[DEBUG] Falling back to sample data since no emails were loaded from database")
        examples = sample_data
else:
    print("[DEBUG] Using sample data for evaluation")
    examples = sample_data

print(f"[DEBUG] Loaded {len(examples)} email examples for evaluation")

if not examples:
    print("[ERROR] No examples available for evaluation")
    sys.exit(1)

# Initialize the EmailSummarizer
summarizer = EmailSummarizer()

print("\n--- Starting evaluation ---\n")

all_rouge_scores = []
all_bleu_scores = []
all_f1_scores = []
successful_evaluations = 0

for i, ex in enumerate(examples):
    print(f"[DEBUG] Processing example {i+1}/{len(examples)}")

    try:
        # Use only the email body for summarization (not the full thread)
        email_body = ex.get('email_body', extract_email_body(ex['thread']))

        # Generate summary from email body only
        auto_sum = summarizer.summarize_email(email_body)

        if not auto_sum or not auto_sum.strip():
            print(f"[WARNING] Empty summary generated for example {i+1}")
            auto_sum = "No summary generated"

        # Calculate ROUGE scores safely (compare generated summary with reference)
        rouge_scores = safe_rouge_score(auto_sum, ex["summary"])
        all_rouge_scores.append(rouge_scores)

        # Calculate BLEU scores safely (compare generated summary with reference)
        bleu_scores = safe_bleu_score(auto_sum, ex["summary"])
        all_bleu_scores.append(bleu_scores)

        # Calculate F1 score (compare generated summary with email body)
        f1_score = safe_f1_score(auto_sum, email_body)
        all_f1_scores.append(f1_score)

        successful_evaluations += 1

        # Print detailed results if verbose mode is enabled
        if args.verbose:
            print_detailed_scores(
                rouge_scores, bleu_scores, f1_score,
                ex.get('email_id', 'N/A'),
                email_body, ex['summary'], auto_sum
            )
        else:
            # Print summary results
            rouge_f1 = rouge_scores['rouge-1']['f']
            bleu_1 = bleu_scores['bleu-1']
            print(f"Example {i+1}: ROUGE-1 F1={rouge_f1:.4f}, BLEU-1={bleu_1:.4f}, TF-IDF F1={f1_score:.4f}")

    except Exception as e:
        print(f"[ERROR] Failed to process example {i+1}: {e}")
        continue

print(f"\n--- Evaluation Complete ---")
print(f"Successfully evaluated {successful_evaluations}/{len(examples)} examples\n")

# Calculate and display average scores
if all_rouge_scores and all_bleu_scores and all_f1_scores:
    avg_rouge, avg_bleu, avg_f1 = calculate_averages(all_rouge_scores, all_bleu_scores, all_f1_scores)

    print("=== AVERAGE SCORES ===")
    print("\nROUGE Scores:")
    for metric, scores in avg_rouge.items():
        print(f"  {metric.upper()}: R={scores['r']:.4f}, P={scores['p']:.4f}, F1={scores['f']:.4f}")

    print("\nBLEU Scores:")
    for metric, score in avg_bleu.items():
        print(f"  {metric.upper()}: {score:.4f}")

    print(f"\nTF-IDF F1 Score: {avg_f1:.4f}")

    # Summary statistics
    print(f"\n=== SUMMARY ===")
    print(f"Best performing metric: ROUGE-1 F1 = {avg_rouge['rouge-1']['f']:.4f}")
    print(f"Overall BLEU-4 score: {avg_bleu['bleu-4']:.4f}")
    print(f"Overall TF-IDF F1 score: {avg_f1:.4f}")

    # Check for potential issues
    zero_rouge_count = sum(1 for scores in all_rouge_scores if scores['rouge-1']['f'] == 0.0)
    zero_bleu_count = sum(1 for scores in all_bleu_scores if scores['bleu-1'] == 0.0)
    zero_f1_count = sum(1 for score in all_f1_scores if score == 0.0)

    if zero_rouge_count > 0:
        print(f"[WARNING] {zero_rouge_count}/{len(all_rouge_scores)} examples had zero ROUGE scores")
    if zero_bleu_count > 0:
        print(f"[WARNING] {zero_bleu_count}/{len(all_bleu_scores)} examples had zero BLEU scores")
    if zero_f1_count > 0:
        print(f"[WARNING] {zero_f1_count}/{len(all_f1_scores)} examples had zero F1 scores")

    if zero_rouge_count > len(all_rouge_scores) * 0.5:
        print("[RECOMMENDATION] Consider improving reference summaries or checking summarizer output quality")

else:
    print("[ERROR] No scores to average, evaluation failed.")
