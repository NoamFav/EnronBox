import requests
import json
from typing import Dict, Any, Optional


class OllamaService:
    """Service for interacting with the Ollama API to generate auto-replies."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama service.
        
        Args:
            base_url: The base URL for the Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url
        
    def generate_reply(self, 
                      email_content: str, 
                      model: str = "llama3", 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate an auto-reply for the given email content using Ollama.
        
        Args:
            email_content: The content of the email to generate a reply for
            model: The Ollama model to use (default: llama3)
            system_prompt: Optional system prompt to guide the model
            temperature: Controls randomness (default: 0.7)
            
        Returns:
            Dict containing the generated reply and metadata
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
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
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
                        "eval_duration": result.get("eval_duration", 0)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status code {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to communicate with Ollama API: {str(e)}"
            } 