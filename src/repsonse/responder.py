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
