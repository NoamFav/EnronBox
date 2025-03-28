#!/bin/bash

# Activate fail-fast mode
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Default values
MAX_EMAILS=5000

# Help menu
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: ./run.sh [--max_emails N]"
    echo ""
    echo "Options:"
    echo "  --max_emails N     Load N emails from the Enron dataset (default: 1000)"
    exit 0
fi

# Parse args
while [[ "$#" -gt 0 ]]; do
    case $1 in
    --max_emails)
        MAX_EMAILS="$2"
        shift
        ;;
    *)
        echo "❌ Unknown argument: $1"
        exit 1
        ;;
    esac
    shift
done

# Ensure requirements are installed
echo -e "${GREEN}📦 Checking Python dependencies...${NC}"
pip install -r requirements.txt >/dev/null

# Launch the shell
echo -e "${GREEN}🚀 Launching Enron Email Intelligence Shell...${NC}"
python3 src/main.py --max_emails "$MAX_EMAILS"
