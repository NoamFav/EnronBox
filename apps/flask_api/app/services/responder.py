from typing import Dict, Any, Optional
from app.services.ollama_service import OllamaService
import requests.exceptions
import os


class EmailResponder:
    """Service for generating auto-replies to emails."""

    def __init__(self, ollama_url: str = None):
        """
        Initialize the email responder.

        Args:
            ollama_url: The URL for the Ollama API
        """
        # Use environment variable if available, otherwise use default
        if ollama_url is None:
            ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

        # Strip any quotes that might be present in the URL
        if isinstance(ollama_url, str):
            ollama_url = ollama_url.strip('"\'')

        self.ollama_service = OllamaService(base_url=ollama_url)

    def generate_reply(self,
                      email_content: str,
                      email_subject: Optional[str] = None,
                      sender_name: Optional[str] = None,
                      model: str = "llama3.2",
                      temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate an auto-reply for the given email.

        Args:
            email_content: The content of the email to reply to
            email_subject: Optional subject of the email
            sender_name: Optional name of the sender
            model: The Ollama model to use
            temperature: Controls randomness in generation

        Returns:
            Dict containing the generated reply and metadata

        Raises:
            requests.exceptions.ConnectionError: If cannot connect to Ollama
            requests.exceptions.Timeout: If the request times out
        """
        # Format the prompt with all available information
        prompt = self._format_prompt(email_content, email_subject, sender_name)

        # Generate system prompt
        system_prompt = self._create_system_prompt(email_subject)

        try:
            # Call Ollama service to generate the reply
            result = self.ollama_service.generate_reply(
                email_content=prompt,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature
            )

            return result

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            # Re-raise these specific exceptions to be handled by the route
            raise e

    def _format_prompt(self,
                      content: str,
                      subject: Optional[str] = None,
                      sender: Optional[str] = None) -> str:
        """Format the prompt for the LLM with all available email information."""
        prompt_parts = []

        if subject:
            prompt_parts.append(f"Subject: {subject}")

        if sender:
            prompt_parts.append(f"From: {sender}")

        prompt_parts.append("\n" + content)
        prompt_parts.append("\n\nPlease generate a professional and appropriate reply to this email.")

        return "\n".join(prompt_parts)

    def _create_system_prompt(self, subject: Optional[str] = None) -> str:
        """Create a system prompt based on email context."""
        base_prompt = (
            "You are a research email assistant that generates professional, concise, "
            "and appropriate replies to emails. Keep your responses clear, "
            "relevant, and to the point, also ignore controversy that a company might've been implied to"
            ". Format your response as a proper email reply "
            "without including any email headers like 'To:', 'From:', or 'Subject:'."
            " When specifying the sender's regards at the end of the response make sure to always say your"
            " name as [Your Name] and the company as [Company Name]. "
        )

        if subject and "urgent" in subject.lower():
            base_prompt += " This is an urgent email, so acknowledge the urgency in your response."

        return base_prompt
