#!/usr/bin/env bash

set -e

# Download Enron dataset if needed
if [ ! -d "maildir" ]; then
    bash bin/download_enron.sh
else
    echo "Maildir already exists."
fi

# Generate the SQLite database
bash bin/generate_db.sh

# Run the Frontend and create the app (dmg or exe)
npm --prefix ./apps/enron_classifier install
npm --prefix ./apps/enron_classifier run tauri build

open -a EnronClassifier

# Move to Flask API directory
cd apps/flask_api

# Export environment variables
export DB_PATH="../SQLite_db/enron.db"
export OLLAMA_URL="http://localhost:11434"

# Confirm environment variables
echo "Using DB_PATH: $DB_PATH"
echo "Using OLLAMA_URL: $OLLAMA_URL"

# Install dependencies
echo "Installing dependencies..."
if command -v pip3 >/dev/null 2>&1; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt

# Start the Flask server
echo "Starting Flask server..."
flask run --host=0.0.0.0 --port=5050
