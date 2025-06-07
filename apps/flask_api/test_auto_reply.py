#!/usr/bin/env python
"""
Test script for the Ollama-powered auto-reply feature.
This script sends a sample email to the Flask API and displays the generated reply.
"""

import requests
import json
import sys
import time
import os
import platform

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:5050/api/respond").strip('"\'')
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").strip('"\'')
# Increased timeout for LLM processing (first-time model loading can take longer)
API_TIMEOUT = 60


# Sample emails for testing
SAMPLE_EMAILS = [
    {
        "subject": "Meeting Tomorrow",
        "content": "Hi Team,\n\nJust a reminder that we have a project status meeting tomorrow at 10 AM in the main conference room. Please prepare your updates and bring any relevant materials.\n\nBest regards,\nJohn"
    },
    {
        "subject": "URGENT: Server Downtime Issue",
        "content": "Hello Support Team,\n\nWe're experiencing critical downtime on our main production server. This is affecting all customer operations. We need immediate assistance to resolve this issue.\n\nError logs show connection timeout errors starting around 3:30 PM today.\n\nPlease advise on next steps.\n\nRegards,\nSarah"
    },
    {
        "subject": "Question about the new feature",
        "content": "Hi Dev Team,\n\nI was testing the new dashboard feature and noticed that the export functionality doesn't seem to be working correctly. When I try to export to CSV, the file is empty.\n\nIs this a known issue? Any timeline on when it might be fixed?\n\nThanks,\nMike"
    }
]

def print_system_info():
    """Print system information to help with debugging."""
    print("\n" + "="*50)
    print("SYSTEM INFORMATION")
    print("="*50)
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Flask API URL: {API_URL}")
    print(f"API Timeout: {API_TIMEOUT} seconds")
    
    # Check if running in Docker
    in_docker = os.path.exists("/.dockerenv")
    print(f"Running in Docker: {'Yes' if in_docker else 'No'}")
    
    if platform.system() == "Windows":
        print("\nNOTE: On Windows, if using Docker, make sure Ollama is accessible via 'host.docker.internal'")
    print("="*50 + "\n")

def check_ollama_running():
    """Check if Ollama is running and available."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Ollama is running at {OLLAMA_URL} with available models: {', '.join(m['name'] for m in models)}")
                return True
            else:
                print(f"⚠️ Ollama is running at {OLLAMA_URL} but no models are available. Please pull a model first.")
                print("   Run: ollama pull llama3")
                return False
        else:
            print(f"⚠️ Ollama API at {OLLAMA_URL} returned unexpected response: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_URL}. Please check if Ollama is running.")
        print("   Run: ollama serve")
        print("\nTroubleshooting tips:")
        print("1. If using Docker, make sure the OLLAMA_URL environment variable is set correctly")
        print("2. On Windows with Docker, use 'http://host.docker.internal:11434' as the URL")
        print("3. On macOS with Docker, use 'http://host.docker.internal:11434' as the URL")
        print("4. On Linux with Docker, you might need to use the host's IP address")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Ollama API request to {OLLAMA_URL} timed out. The service might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama status at {OLLAMA_URL}: {str(e)}")
        return False

def check_flask_api_running():
    """Check if the Flask API is running and available."""
    try:
        # Try to access a known endpoint
        api_base = API_URL.split('/api/')[0]
        response = requests.get(f"{api_base}/api/users", timeout=5)
        if response.status_code in (200, 404):  # Either response means the server is running
            print(f"✅ Flask API is running at {API_URL}")
            return True
        else:
            print(f"⚠️ Flask API at {API_URL} returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Flask API at {API_URL}. Please start the Flask API first.")
        print("   Run: docker compose up --build")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Flask API request to {API_URL} timed out. The service might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Error checking Flask API status at {API_URL}: {str(e)}")
        return False

def test_auto_reply(email_idx=0):
    """Test the auto-reply feature with a sample email."""
    print_system_info()
    
    # Check if Flask API is running first
    if not check_flask_api_running():
        return
    
    # Check if Ollama is running, but continue even if it's not
    ollama_running = check_ollama_running()
    if not ollama_running:
        print("⚠️ Continuing with the test even though Ollama appears to be unavailable.")
        print("   The Flask API should handle this error gracefully.")
    
    # Get the sample email
    email = SAMPLE_EMAILS[email_idx]
    
    print("\n" + "="*50)
    print(f"📧 SAMPLE EMAIL {email_idx + 1}")
    print("="*50)
    print(f"Subject: {email['subject']}")
    print(f"{email['content']}")
    print("="*50 + "\n")
    
    # Prepare the request
    payload = {
        "content": email["content"],
        "subject": email["subject"],
        "sender": "test@example.com",
        "model": "llama3.2",  # Change this to any model you have pulled in Ollama
        "temperature": 0.7
    }
    
    print("Generating auto-reply... (this may take a few seconds)")
    print(f"Timeout set to {API_TIMEOUT} seconds (first-time model loading may take longer)")
    start_time = time.time()
    
    # Send the request
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=API_TIMEOUT
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("\n" + "="*50)
                print("✅ AUTO-REPLY GENERATED")
                print("="*50)
                print(result["reply"])
                print("="*50)
                print(f"\nGenerated in {elapsed_time:.2f} seconds")
                if "metadata" in result:
                    print(f"Model: {result['metadata'].get('model', 'unknown')}")
            else:
                print("\n" + "="*50)
                print("⚠️ API RETURNED ERROR")
                print("="*50)
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Details: {result.get('details', 'No additional details')}")
                print("="*50)
                print("\nThis error might be because Ollama is not running or the model is unavailable.")
                print("The Flask API handled the error gracefully and returned a proper error response.")
                
                # Print additional debugging information for URL-related errors
                error_msg = result.get('error', '')
                if 'No connection adapters were found' in error_msg or 'URL' in error_msg:
                    print("\n" + "="*50)
                    print("🔍 DEBUGGING URL FORMAT ISSUE")
                    print("="*50)
                    print("The error appears to be related to URL formatting.")
                    print(f"Current OLLAMA_URL: {OLLAMA_URL}")
                    print("\nPossible solutions:")
                    print("1. Set OLLAMA_URL without quotes:")
                    print("   export OLLAMA_URL=http://localhost:11434")
                    print("2. For Docker on Windows, try:")
                    print("   export OLLAMA_URL=http://host.docker.internal:11434")
                    print("3. Check the Flask API code to ensure URLs are properly handled")
                    print("="*50)
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            print(response.text)
            print("\nThis might indicate an issue with the Flask API itself, not just Ollama.")
    except requests.exceptions.Timeout:
        print("\n" + "="*50)
        print("❌ API REQUEST TIMED OUT")
        print("="*50)
        print(f"Request timed out after {API_TIMEOUT} seconds")
        print("\nPossible solutions:")
        print("1. The model may be loading for the first time (can take several minutes)")
        print("2. Try increasing the API_TIMEOUT value at the top of this script")
        print("3. Check if your system has enough resources to run the model")
        print("4. Verify that Ollama is not overloaded with other requests")
        print("="*50)
    except requests.exceptions.ConnectionError:
        print("\n" + "="*50)
        print("❌ CONNECTION ERROR")
        print("="*50)
        print("Connection error when communicating with the Flask API")
        print("The Flask API might have crashed while processing the request.")
        print("This often happens when the API doesn't properly handle Ollama connection issues.")
        print("\nPossible solutions:")
        print("1. Check if the Flask API is still running")
        print("2. Verify that the API_URL is correct")
        print("3. Check the Flask API logs for errors")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print("❌ UNEXPECTED ERROR")
        print("="*50)
        print(f"Failed to communicate with API: {str(e)}")
        print("="*50)

if __name__ == "__main__":
    # Get email index from command line argument or use default (0)
    email_idx = 0
    if len(sys.argv) > 1:
        try:
            email_idx = int(sys.argv[1])
            if email_idx < 0 or email_idx >= len(SAMPLE_EMAILS):
                print(f"Invalid email index. Please use a number between 0 and {len(SAMPLE_EMAILS) - 1}")
                sys.exit(1)
        except ValueError:
            print("Invalid argument. Please provide a number for the email index.")
            sys.exit(1)
    
    test_auto_reply(email_idx) 