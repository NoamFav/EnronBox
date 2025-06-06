import os
import requests
import json
import sys

def test_ollama_connection():
    """Test the connection to Ollama API and verify URL format."""
    
    # Get Ollama URL from environment or use default
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    
    # Strip any quotes that might be present
    ollama_url = ollama_url.strip('"\'')
    
    print(f"Testing connection to Ollama at: {ollama_url}")
    
    # First, check if Ollama is running by querying the list of models
    try:
        models_url = f"{ollama_url}/api/tags"
        print(f"Requesting models from: {models_url}")
        
        response = requests.get(models_url, timeout=5)
        response.raise_for_status()
        
        models_data = response.json()
        print("\n✅ Successfully connected to Ollama!")
        print(f"Available models: {', '.join([m['name'] for m in models_data['models']])}")
        
        # Test a simple generation to verify the full API works
        print("\nTesting a simple generation...")
        
        generate_url = f"{ollama_url}/api/generate"
        print(f"Sending request to: {generate_url}")
        
        payload = {
            "model": "llama3.2",  # Change to a model you have installed
            "prompt": "Hello, how are you?",
            "system": "You are a helpful assistant.",
            "stream": False
        }
        
        print("This may take up to 30 seconds for the first generation...")
        
        response = requests.post(
            generate_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30  # Increased timeout to 30 seconds
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("\n✅ Successfully generated a response!")
        print(f"Response: {result.get('response', '')[:100]}...")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {str(e)}")
        print("\nPossible solutions:")
        print("1. Make sure Ollama is running")
        print("2. If using Docker, ensure host.docker.internal resolves correctly")
        print("3. Check firewall settings")
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP error: {e.response.status_code} - {e.response.text}")
        return False
    
    except requests.exceptions.Timeout as e:
        print(f"\n❌ Timeout error: {str(e)}")
        print("\nPossible solutions:")
        print("1. The model may be loading for the first time (can take several minutes)")
        print("2. Try increasing the timeout value")
        print("3. Check if your system has enough resources to run the model")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ollama_connection()
    sys.exit(0 if success else 1) 