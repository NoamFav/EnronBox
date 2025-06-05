#!/usr/bin/env python
"""
Test script for the Ollama-powered auto-reply feature.
This script sends a sample email to the Flask API and displays the generated reply.
"""

import requests
import json
import sys
import time

# Configuration
API_URL = "http://localhost:5050/api/respond"
OLLAMA_URL = "http://localhost:11434"

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

def check_ollama_running():
    """Check if Ollama is running and available."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Ollama is running with available models: {', '.join(m['name'] for m in models)}")
                return True
            else:
                print("⚠️ Ollama is running but no models are available. Please pull a model first.")
                print("   Run: ollama pull llama3")
                return False
        else:
            print("⚠️ Ollama API returned unexpected response")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Please start Ollama first.")
        print("   Run: ollama serve")
        return False

def check_flask_api_running():
    """Check if the Flask API is running and available."""
    try:
        # Try to access a known endpoint
        response = requests.get("http://localhost:5050/api/users")
        if response.status_code in (200, 404):  # Either response means the server is running
            print("✅ Flask API is running")
            return True
        else:
            print(f"⚠️ Flask API returned unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask API is not running. Please start the Flask API first.")
        print("   Run: docker compose up --build")
        return False

def test_auto_reply(email_idx=0):
    """Test the auto-reply feature with a sample email."""
    if not check_ollama_running() or not check_flask_api_running():
        return
    
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
        "model": "llama3",  # Change this to any model you have pulled in Ollama
        "temperature": 0.7
    }
    
    print("Generating auto-reply... (this may take a few seconds)")
    start_time = time.time()
    
    # Send the request
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
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
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ API request failed with status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Failed to communicate with API: {str(e)}")

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