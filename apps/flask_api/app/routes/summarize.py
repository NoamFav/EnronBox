from flask import Blueprint, request, jsonify
from app.services.summarizer import EmailSummarizer

summarize_bp = Blueprint("summarize", __name__)

from flask import request, jsonify, make_response


@summarize_bp.route("", methods=["POST"])
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
    data = request.get_json()

    if not data or "email_text" not in data:
        return jsonify({"error": "Missing required parameter: email_text"}), 400

    email_text = data.get("email_text")
    num_sentences = data.get("num_sentences", 3)

    summarizer = EmailSummarizer()
    summary = summarizer.summarize_email(email_text, num_sentences)

    return jsonify({"summary": summary})
