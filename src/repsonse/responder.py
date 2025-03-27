"""
responder.py - Automated email reply generator

Generates context-aware email replies based on classification, sentiment, and urgency.
Uses template-based responses that can be customized for different scenarios.
"""

# Template database - could be moved to a config file or external template system
RESPONSE_TEMPLATES = {
    # Professional/formal responses
    "professional": {
        "positive": {
            "template": "Dear {sender},\n\nThank you for your email regarding {topic}. "
                        "We're pleased to hear about {positive_aspect} and would be happy to "
                        "help with this matter.\n\nBest regards,\n{signature}",
            "placeholders": ["topic", "positive_aspect"]
        },
        "neutral": {
            "template": "Dear {sender},\n\nWe acknowledge receipt of your email about {topic}. "
                        "One of our team members will review your inquiry and respond "
                        "shortly.\n\nRegards,\n{signature}",
            "placeholders": ["topic"]
        },
        "negative": {
            "template": "Dear {sender},\n\nWe appreciate you reaching out about {topic}. "
                        "We sincerely apologize for {negative_aspect} and are looking into "
                        "this matter urgently.\n\nSincerely,\n{signature}",
            "placeholders": ["topic", "negative_aspect"]
        }
    },

    # Casual/informal responses
    "casual": {
        "positive": {
            "template": "Hi {sender},\n\nThanks for your note! Great to hear about {topic}. "
                        "Let me know if you need anything else.\n\nCheers,\n{signature}",
            "placeholders": ["topic"]
        },
        "neutral": {
            "template": "Hi {sender},\n\nGot your email about {topic}. I'll look into this and "
                        "get back to you soon.\n\nBest,\n{signature}",
            "placeholders": ["topic"]
        },
        "negative": {
            "template": "Hi {sender},\n\nThanks for flagging this. Really sorry about {negative_aspect}. "
                        "We're working on fixing this ASAP.\n\nThanks for your patience,\n{signature}",
            "placeholders": ["topic", "negative_aspect"]
        }
    },

    # Urgent responses
    "urgent": {
        "template": "Dear {sender},\n\nWe've received your urgent message regarding {topic} and "
                    "are prioritizing this matter. You can expect a response by {timeframe}.\n\n"
                    "For immediate assistance, please contact {contact}.\n\n"
                    "Best regards,\n{signature}",
        "placeholders": ["topic", "timeframe", "contact"]
    },

    # Out of office/automatic responses
    "out_of_office": {
        "template": "Dear {sender},\n\nThank you for your email. I'm currently out of the office "
                    "with limited access to email until {return_date}. For urgent matters, "
                    "please contact {contact}.\n\nI'll respond to your message about {topic} "
                    "when I return.\n\nBest regards,\n{signature}",
        "placeholders": ["return_date", "contact", "topic"]
    }
}

# Default signature
DEFAULT_SIGNATURE = "Your Name\nYour Position\nYour Company"

def generate_reply(email: dict, prediction: dict) -> str:
    """
    Generates an appropriate reply based on email content and classification.

    Args:
        email: Dictionary containing email details with keys:
            - 'sender': Sender's name/email
            - 'subject': Email subject
            - 'body': Email content
            - 'thread': Thread history (if available)

        prediction: Dictionary containing classification results with keys:
            - 'category': Primary category (e.g., 'professional', 'casual')
            - 'sentiment': 'positive', 'neutral', or 'negative'
            - 'urgency': Boolean indicating urgent message
            - 'entities': Extracted named entities (optional)
            - 'summary': Thread summary (optional)

    Returns:
        str: Generated reply text
    """
    # Determine which template to use
    if prediction.get('urgency', False):
        template_data = RESPONSE_TEMPLATES['urgent']
        template = template_data['template']
        placeholders = template_data['placeholders']
    else:
        category = prediction.get('category', 'professional')
        sentiment = prediction.get('sentiment', 'neutral')

        # Fallback to professional/neutral if category/sentiment not found
        category_templates = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES['professional'])
        template_data = category_templates.get(sentiment, category_templates['neutral'])
        template = template_data['template']
        placeholders = template_data.get('placeholders', [])

    # Prepare template variables
    template_vars = {
        'sender': email.get('sender', 'Sir/Madam'),
        'signature': DEFAULT_SIGNATURE,
        'topic': email.get('subject', 'this matter'),
        'positive_aspect': extract_positive_aspect(email.get('body', '')),
        'negative_aspect': extract_negative_aspect(email.get('body', '')),
        'timeframe': 'end of day' if prediction.get('urgency') else '48 hours',
        'contact': 'support@company.com',
        'return_date': 'next Monday'
    }

    # Add any extracted entities if available
    if 'entities' in prediction:
        template_vars.update(prediction['entities'])

    # Fill the template
    try:
        reply = template.format(**template_vars)
    except KeyError as e:
        # Fallback if missing some placeholder data
        for ph in placeholders:
            if ph not in template_vars:
                template_vars[ph] = 'this matter'
        reply = template.format(**template_vars)

    return reply

def extract_positive_aspect(body: str) -> str:
    """
    Helper to extract positive aspects from email body for template filling.
    """
    # This could be enhanced with more sophisticated NLP
    positive_phrases = [
        'great', 'excellent', 'happy', 'pleased', 'thank you',
        'thanks', 'appreciate', 'wonderful', 'awesome'
    ]

    for phrase in positive_phrases:
        if phrase in body.lower():
            return phrase

    return 'your positive feedback'

def extract_negative_aspect(body: str) -> str:
    """
    Helper to extract negative aspects from email body for template filling.
    """
    # This could be enhanced with more sophisticated NLP
    negative_phrases = [
        'problem', 'issue', 'concern', 'disappointed',
        'unhappy', 'angry', 'frustrated', 'not working'
    ]

    for phrase in negative_phrases:
        if phrase in body.lower():
            return f'the {phrase}'

    return 'this situation'
