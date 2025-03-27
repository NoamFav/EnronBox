#!/bin/bash

# Set the Enron dataset URL
ENRON_URL="https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
OUTPUT_FILE="enron_maildir.tar.gz"

# Download the dataset
echo "Downloading Enron email dataset..."
curl -L -o "$OUTPUT_FILE" "$ENRON_URL"

# Verify the download
if [ -f "$OUTPUT_FILE" ]; then
    echo "Download complete: $OUTPUT_FILE"
else
    echo "Error: Download failed!"
    exit 1
fi

# Extract the dataset
echo "Extracting dataset..."
tar -xvzf "$OUTPUT_FILE"

# Cleanup
echo "Cleaning up..."
rm "$OUTPUT_FILE"

echo "Enron dataset is ready"
