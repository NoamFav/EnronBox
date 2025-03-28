"""
responder.py - Integrated with enron_classifier output analysis
"""

import random
from typing import Dict, Any


class EmailResponder:
    def __init__(self, classifier):
        """Initialize with an EnronEmailClassifier instance"""
        self.classifier = classifier

        # Configure response templates
        self.templates = {
            "work": self._init_work_templates(),
            "personal": self._init_personal_templates(),
            "default": self._init_default_templates(),
        }

    def generate_reply(self, email: Dict[str, Any]) -> str:
        """
        Generate response by:
        1. Getting prediction from enron_classifier
        2. Analyzing the output
        3. Selecting appropriate template
        """
        # Step 1: Get classifier prediction
        prediction = self.classifier.predict(email)
        print("\n=== Classifier Output ===")
        print(f"Category: {prediction.get('category')}")
        print(f"Sentiment: {prediction.get('sentiment')}")
        print(f"Urgency: {prediction.get('urgency')}")

        # Step 2: Analyze prediction
        category = prediction.get("category", "default").lower()
        sentiment = self._analyze_sentiment(prediction.get("sentiment", {}))
        is_urgent = prediction.get("urgency", False)

        # Step 3: Generate response
        context = self._prepare_context(email, prediction)
        template = self._select_template(category, sentiment, is_urgent)

        return template.format(**context)

    # Analysis and template selection methods
    def _analyze_sentiment(self, sentiment_data: Dict[str, float]) -> str:
        """Convert polarity score to sentiment category"""
        polarity = sentiment_data.get("polarity", 0)
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        return "neutral"

    def _select_template(self, category, sentiment, is_urgent) -> str:
        """Select template with fallback logic"""
        # Try category-specific template first
        templates = self.templates.get(category, self.templates["default"])

        # Handle urgent messages specially
        if is_urgent:
            urgent_template = getattr(self, f"_urgent_{category}_template", None)
            if urgent_template:
                return urgent_template()

        # Fallback to neutral if no sentiment templates exist
        return random.choice(templates.get(sentiment, templates["neutral"]))

    def _prepare_context(self, email, prediction) -> Dict[str, str]:
        """Prepare variables for template formatting"""
        return {
            "sender": self._extract_name(email.get("sender", "")),
            "subject": email.get("subject", "your message"),
            "signature": "Your Name\nYour Company",
            "timeframe": (
                "within 24 hours"
                if prediction.get("urgency")
                else "in 2-3 business days"
            ),
            "positive_phrase": self._extract_phrase(
                email["body"], ["great", "excellent", "thank"]
            ),
            "negative_phrase": self._extract_phrase(
                email["body"], ["problem", "issue", "concern"]
            ),
        }

    # Template definitions
    def _init_work_templates(self):
        return {
            "positive": [
                "Dear {sender},\n\nThank you for your positive feedback about {subject}.\n"
                "We're delighted that {positive_phrase} and will continue to maintain\n"
                "this standard of service.\n\n"
                "Best regards,\n{signature}",
                "Hello {sender},\n\nWe appreciate your kind words regarding {subject}.\n"
                "It's rewarding to know that {positive_phrase}. Should you need\n"
                "anything further, don't hesitate to reach out.\n\n"
                "Kind regards,\n{signature}",
            ],
            "neutral": [
                "Dear {sender},\n\nWe acknowledge receipt of your email regarding {subject}.\n"
                "This matter has been logged (Ref: {reference_number}) and will be\n"
                "addressed within {timeframe}.\n\n"
                "Sincerely,\n{signature}",
                "Hello {sender},\n\nYour message about {subject} has been received.\n"
                "Our team is reviewing your inquiry and will respond by\n"
                "{timeframe}.\n\n"
                "Regards,\n{signature}",
            ],
            "negative": [
                "Dear {sender},\n\nWe sincerely apologize for {negative_phrase}.\n"
                "This is not our standard, and we're taking immediate steps to\n"
                "{corrective_action}. For direct assistance, contact {contact}.\n\n"
                "Our apologies,\n{signature}",
                "Hello {sender},\n\nWe regret the inconvenience caused by {negative_phrase}.\n"
                "A resolution team has been assigned and will update you by\n"
                "{timeframe}.\n\n"
                "Sincerely,\n{signature}",
            ],
            "urgent": [
                "URGENT: {subject}\n\nDear {sender},\n\nWe've prioritized your request and\n"
                "are addressing it urgently. Expect an update by {timeframe}.\n"
                "For immediate support: {contact}.\n\n"
                "Best regards,\n{signature}"
            ],
        }

    def _init_personal_templates(self):
        return {
            "positive": [
                "Hi {first_name},\n\nThanks for your lovely message! I'm really glad\n"
                "you enjoyed {positive_phrase}. Let's {suggestion} soon!\n\n"
                "Cheers,\n{signature}",
                "Hey {first_name},\n\nGreat to hear from you! I'm thrilled you liked\n"
                "{positive_phrase}. We should definitely {suggestion} when you're free.\n\n"
                "Best,\n{signature}",
            ],
            "neutral": [
                "Hi {first_name},\n\nThanks for your note about {subject}.\n"
                "I'll look into this and get back to you soon.\n\n"
                "Talk soon,\n{signature}",
                "Hey {first_name},\n\nGot your message about {subject}.\n"
                "Let me check and I'll circle back to you.\n\n"
                "Best,\n{signature}",
            ],
            "negative": [
                "Hi {first_name},\n\nI'm really sorry about {negative_phrase}.\n"
                "Let me know how I can make this right.\n\n"
                "Take care,\n{signature}",
                "Hey {first_name},\n\nMy apologies for {negative_phrase}.\n"
                "How about we {makeup_idea} to make up for it?\n\n"
                "My best,\n{signature}",
            ],
        }

    def _init_default_templates(self):
        return {
            "positive": [
                """Dear {sender},

    Thank you for your message regarding {subject}. We're pleased to hear about
    {positive_phrase} and appreciate you taking the time to share this feedback.

    Should you require any further assistance, please don't hesitate to contact us.

    Best regards,
    {signature}""",
                """Hello {sender},

    We acknowledge your positive comments about {subject}. It's rewarding to know that
    {positive_phrase}.

    We value your input and will share this with the relevant team.

    Kind regards,
    {signature}""",
            ],
            "neutral": [
                """Dear {sender},

    We confirm receipt of your communication concerning {subject}. This matter has been
    forwarded to the appropriate department and will receive attention within
    {timeframe}.

    For reference, your case number is: {reference_number}

    Sincerely,
    {signature}""",
                """Hello {sender},

    Thank you for your email about {subject}. We're currently reviewing your inquiry
    and will provide a response by {timeframe}.

    If you need immediate assistance, please contact {contact}.

    Regards,
    {signature}""",
            ],
            "negative": [
                """Dear {sender},

    We sincerely regret to hear about your experience with {negative_phrase}. Please
    accept our apologies for any inconvenience caused.

    Our team is looking into this matter and will update you by {timeframe}.

    For direct assistance, you may reach us at {contact}.

    With apologies,
    {signature}""",
            ],
        }

    # Demo method using actual classifier
    @classmethod
    def demo(cls, classifier):
        """Run with real classifier output"""
        print("\n=== Running Responder Demo with Real Classifier ===")

        test_emails = [
            {
                "sender": "john.doe@enron.com",
                "subject": "Project Update",
                "body": "The results look excellent! Great work!",
            },
            {
                "sender": "sarah.smith@gmail.com",
                "subject": "Urgent Issue",
                "body": "We have a critical problem with the system!",
            },
        ]

        responder = cls(classifier)
        for email in test_emails:
            print(f"\nProcessing email: {email['subject']}")
            reply = responder.generate_reply(email)
            print("\nGenerated Reply:")
            print(reply)
            print("-" * 50)

    def _extract_name(self, email_address: str) -> str:
        if not email_address:
            return "Sir/Madam"

        # Extract username if it's an email
        username = (
            email_address.split("@")[0] if "@" in email_address else email_address
        )

        # Remove any domain parts if present (e.g., 'kaminski-v@domain' -> 'kaminski-v')
        username = username.split("@")[0]

        # Common Enron username patterns:
        # 1. lastname-firstinitial (kaminski-v)
        # 2. firstname_lastname (jeff.skilling)
        # 3. firstinitiallastname (jskilling)

        # Pattern 1: lastname-firstinitial
        if "-" in username:
            lastname, firstinitial = username.split("-", 1)
            return f"{firstinitial.upper()} {lastname.capitalize()}"

        # Pattern 2: firstname.lastname
        elif "." in username:
            firstname, lastname = username.split(".", 1)
            return f"{firstname.capitalize()} {lastname.capitalize()}"

        # Pattern 3: firstinitial + lastname (jskilling)
        elif len(username) > 1 and not username[1].isupper():
            return f"{username[0].upper()} {username[1:].capitalize()}"

        # Fallback for other patterns
        return username.replace(".", " ").replace("_", " ").title()

    def _extract_phrase(self, text: str, phrase_list: list) -> str:
        if not text or not phrase_list:
            return ""

        text_lower = str(text).lower()
        found_phrases = []

        # Find all matching phrases
        for phrase in phrase_list:
            if phrase.lower() in text_lower:
                # Find the actual occurrence in original text
                start = text_lower.find(phrase.lower())
                end = start + len(phrase)
                found_phrases.append(text[start:end])

        # Return the longest matching phrase for better context
        if found_phrases:
            return max(found_phrases, key=len)

        # Smart fallbacks based on phrase list type
        if any(p in ["great", "excellent", "thank"] for p in phrase_list):
            return "your positive feedback"
        elif any(p in ["problem", "issue", "concern"] for p in phrase_list):
            return "this situation"

        return "this matter"  # Ultimate fallback
