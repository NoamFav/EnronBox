import requests
import json
import os
from typing import Dict, Any, Optional


class OllamaService:
    """Service for interacting with the Ollama API to generate auto-replies."""

    def __init__(self, base_url: str = None):
        """
        Initialize the Ollama service.

        Args:
            base_url: The base URL for the Ollama API (default from env or http://localhost:11434)
        """
        # Use provided URL, environment variable, or default
        if base_url is None:
            base_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

        # Remove any surrounding quotes that might be present in the URL
        self.base_url = base_url.strip("\"'")

    def generate_reply(
        self,
        email_content: str,
        model: str = "llama3.2",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """
        Generate an auto-reply for the given email content using Ollama.

        Args:
            email_content: The content of the email to generate a reply for
            model: The Ollama model to use (default: llama3.2)
            system_prompt: Optional system prompt to guide the model
            temperature: Controls randomness (default: 0.7)
            timeout: Request timeout in seconds (default: 60)

        Returns:
            Dict containing the generated reply and metadata

        Raises:
            requests.exceptions.ConnectionError: If cannot connect to Ollama
            requests.exceptions.Timeout: If the request times out
            requests.exceptions.RequestException: For other request-related errors
        """
        if system_prompt is None:
            system_prompt = (
                "You are an email assistant that generates professional, concise, "
                "and appropriate replies to emails. Keep your responses clear, "
                "relevant, and to the point."
            )

        payload = {
            "model": model,
            "prompt": email_content,
            "system": system_prompt,
            "temperature": temperature,
            "stream": False,
        }

        try:
            api_url = f"{self.base_url}/api/generate"
            response = requests.post(
                api_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=timeout,
            )

            response.raise_for_status()  # Raise exception for 4XX/5XX responses

            result = response.json()
            return {
                "success": True,
                "reply": result.get("response", ""),
                "metadata": {
                    "model": model,
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                },
            }

        except requests.exceptions.ConnectionError as e:
            # Re-raise connection errors to be handled by the caller
            raise e

        except requests.exceptions.Timeout as e:
            # Re-raise timeout errors to be handled by the caller
            raise e

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 0
            error_text = e.response.text if e.response else str(e)

            return {
                "success": False,
                "error": f"Ollama API returned HTTP error {status_code}",
                "details": error_text,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to communicate with Ollama API: {str(e)}",
                "details": f"Unexpected error when calling Ollama API at URL: {api_url}",
            }
