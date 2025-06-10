from flask import Blueprint, request, jsonify
from app.services.responder import EmailResponder
import requests.exceptions
import os

respond_bp = Blueprint("respond", __name__)


@respond_bp.route("", methods=["POST"])
def generate_response():
    """
    Generate an auto-reply for an email using Ollama.

    Expected JSON body:
    {
        "content": "Email content here",
        "subject": "Email subject (optional)",
        "sender": "Sender name (optional)",
        "model": "Ollama model to use (optional, default: llama3.2)",
        "temperature": float (optional, default: 0.7)
    }

    Returns:
    {
        "success": true/false,
        "reply": "Generated reply",
        "metadata": {
            // Model performance metrics
        }
    }
    """
    try:
        data = request.get_json()

        if not data or "content" not in data:
            return (
                jsonify({"success": False, "error": "Missing required field: content"}),
                400,
            )

        # Get Ollama URL from environment and strip any quotes
        ollama_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
        if isinstance(ollama_url, str):
            ollama_url = ollama_url.strip("\"'")

        # Initialize the responder with the cleaned URL
        responder = EmailResponder(ollama_url=ollama_url)

        # Extract parameters from request
        email_content = data.get("content")
        email_subject = data.get("subject")
        sender_name = data.get("sender")
        model = data.get("model", "llama3.2")
        temperature = float(data.get("temperature", 0.7))

        # Generate the reply
        try:
            result = responder.generate_reply(
                email_content=email_content,
                email_subject=email_subject,
                sender_name=sender_name,
                model=model,
                temperature=temperature,
            )

            return jsonify(result)

        except requests.exceptions.ConnectionError:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Failed to connect to Ollama service at {ollama_url}",
                        "details": "Please ensure Ollama is running and accessible",
                    }
                ),
                503,
            )
        except requests.exceptions.Timeout:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Ollama service timed out",
                        "details": "The LLM is taking too long to respond or the service is overloaded",
                    }
                ),
                504,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Failed to generate reply: {str(e)}",
                    "details": "An unexpected error occurred in the API",
                }
            ),
            500,
        )
