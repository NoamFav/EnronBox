#!/usr/bin/env bash

set -e # Exit immediately if a command exits with a non-zero status

# Move to the Flask API directory
cd apps/flask_api

# Determine whether to use pip or pip3
if command -v pip3 >/dev/null 2>&1; then
    PIP_CMD="pip3"
elif command -v pip >/dev/null 2>&1; then
    PIP_CMD="pip"
else
    echo "Neither pip3 nor pip is installed. Please install Python pip."
    exit 1
fi

# Install the dependencies from requirements.txt
echo "Installing dependencies..."
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt

# Run the Flask app
echo "Starting Flask server..."
flask run --host=0.0.0.0 --port=5050
