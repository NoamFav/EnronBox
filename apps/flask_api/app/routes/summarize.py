from flask import Blueprint, request, jsonify
from app.services.summarizer import EmailSummarizer

summarize_bp = Blueprint("summarize", __name__)

from flask import request, jsonify, make_response

@summarize_bp.route("", methods=["POST", "OPTIONS"])
def summarize_email():
    """
    Endpoint to summarize email content

    Expected JSON request:
    {
        "email_text": "The full email text to summarize",
        "num_sentences": 3  # Optional, defaults to 3
    }

    Returns:
    {
        "summary": "Summarized email text"
    }
    """

    # Handle CORS preflight request
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:1420")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    # Handle actual POST request
    data = request.get_json()

    if not data or 'email_text' not in data:
        response = jsonify({"error": "Missing required parameter: email_text"})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:1420")
        return response, 400

    email_text = data.get('email_text')
    num_sentences = data.get('num_sentences', 3)

    summarizer = EmailSummarizer()
    summary = summarizer.summarize_email(email_text, num_sentences)

    response = jsonify({"summary": summary})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:1420")
    return response

