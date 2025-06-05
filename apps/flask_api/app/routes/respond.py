from flask import Blueprint, request, jsonify
from app.services.responder import EmailResponder

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
        "model": "Ollama model to use (optional, default: llama3)",
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
            return jsonify({
                "success": False,
                "error": "Missing required field: content"
            }), 400
            
        # Initialize the responder
        responder = EmailResponder()
        
        # Extract parameters from request
        email_content = data.get("content")
        email_subject = data.get("subject")
        sender_name = data.get("sender")
        model = data.get("model", "llama3")
        temperature = float(data.get("temperature", 0.7))
        
        # Generate the reply
        result = responder.generate_reply(
            email_content=email_content,
            email_subject=email_subject,
            sender_name=sender_name,
            model=model,
            temperature=temperature
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to generate reply: {str(e)}"
        }), 500
