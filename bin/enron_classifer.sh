#!/usr/bin/env bash

set -e # Exit immediately if a command exits with a non-zero status

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Function to download Enron dataset
download_enron() {
    local ENRON_URL="https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
    local OUTPUT_FILE="enron_maildir.tar.gz"

    print_status "Downloading Enron email dataset..."

    if command_exists curl; then
        curl -L --progress-bar -o "$OUTPUT_FILE" "$ENRON_URL"
    elif command_exists wget; then
        wget --progress=bar:force -O "$OUTPUT_FILE" "$ENRON_URL"
    else
        print_error "Neither curl nor wget is available. Please install one of them."
        exit 1
    fi

    # Verify the download
    if [ -f "$OUTPUT_FILE" ]; then
        print_success "Download complete: $OUTPUT_FILE"
    else
        print_error "Download failed!"
        exit 1
    fi

    # Extract the dataset
    print_status "Extracting dataset..."
    tar -xzf "$OUTPUT_FILE"

    # Cleanup
    print_status "Cleaning up download file..."
    rm "$OUTPUT_FILE"

    print_success "Enron dataset is ready"
}

# Function to generate database
generate_database() {
    print_status "Generating SQLite database..."
    if [ -f "apps/SQLite_db/generate_db.py" ]; then
        python3 apps/SQLite_db/generate_db.py
        print_success "Database generated!"
    else
        print_error "Database generation script not found!"
        exit 1
    fi
}

# Function to determine pip command
get_pip_command() {
    if command_exists pip3; then
        echo "pip3"
    elif command_exists pip; then
        echo "pip"
    else
        print_error "Neither pip3 nor pip is installed. Please install Python pip."
        exit 1
    fi
}

# Function to build frontend
build_frontend() {
    local OS=$(detect_os)

    print_status "Building frontend application..."

    # Check if Node.js and npm are installed
    if ! command_exists npm; then
        print_error "npm is not installed. Please install Node.js and npm."
        exit 1
    fi

    # Install dependencies and build
    if [ -d "apps/enron_classifier" ]; then
        print_status "Installing frontend dependencies..."
        npm --prefix ./apps/enron_classifier install

        print_status "Building Tauri application..."
        npm --prefix ./apps/enron_classifier run tauri build

        # Try to open the application based on OS
        if [ "$OS" = "macos" ]; then
            if [ -d "apps/enron_classifier/src-tauri/target/release/bundle/macos" ]; then
                print_status "Opening application on macOS..."
                open -a EnronClassifier 2>/dev/null || print_warning "Could not auto-open application. Please open it manually."
            fi
        elif [ "$OS" = "linux" ]; then
            print_success "Application built successfully. Check the target directory for the executable."
        fi
    else
        print_error "Frontend directory not found!"
        exit 1
    fi
}

# Function to setup and run Flask API
run_flask_api() {
    print_status "Setting up Flask API..."

    # Move to Flask API directory
    if [ ! -d "apps/flask_api" ]; then
        print_error "Flask API directory not found!"
        exit 1
    fi

    cd apps/flask_api

    # Export environment variables
    export DB_PATH="../SQLite_db/enron.db"
    export OLLAMA_URL="http://localhost:11434"

    print_status "Using DB_PATH: $DB_PATH"
    print_status "Using OLLAMA_URL: $OLLAMA_URL"

    # Get pip command
    local PIP_CMD=$(get_pip_command)

    # Install dependencies
    print_status "Installing Python dependencies..."
    $PIP_CMD install --upgrade pip

    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
    else
        print_error "requirements.txt not found!"
        exit 1
    fi

    # Check if Ollama is running
    print_status "Checking if Ollama is running..."
    if curl -s "$OLLAMA_URL" >/dev/null 2>&1; then
        print_success "Ollama is running at $OLLAMA_URL"
    else
        print_warning "Ollama doesn't seem to be running at $OLLAMA_URL"
        print_warning "Please make sure Ollama is installed and running before using the classifier"
    fi

    # Start the Flask server
    print_status "Starting Flask server on http://0.0.0.0:5050..."
    flask run --host=0.0.0.0 --port=5050
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --download-only    Only download and extract the Enron dataset"
    echo "  --db-only         Only generate the database"
    echo "  --frontend-only   Only build the frontend application"
    echo "  --api-only        Only run the Flask API server"
    echo "  --skip-frontend   Skip building the frontend application"
    echo "  --help, -h        Show this help message"
    echo ""
    echo "Default behavior: Run the complete setup (download, database, frontend, API)"
}

# Main execution
main() {
    local OS=$(detect_os)
    local SKIP_FRONTEND=false

    print_status "Detected OS: $OS"
    print_status "Starting Enron Classifier setup..."

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
        --download-only)
            if [ ! -d "maildir" ]; then
                download_enron
            else
                print_warning "Maildir already exists. Skipping download."
            fi
            exit 0
            ;;
        --db-only)
            generate_database
            exit 0
            ;;
        --frontend-only)
            build_frontend
            exit 0
            ;;
        --api-only)
            run_flask_api
            exit 0
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --help | -h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        esac
    done

    # Step 1: Download Enron dataset if needed
    if [ ! -d "maildir" ]; then
        download_enron
    else
        print_warning "Maildir already exists. Skipping download."
    fi

    # Step 2: Generate the SQLite database
    generate_database

    # Step 3: Build frontend (unless skipped)
    if [ "$SKIP_FRONTEND" = false ]; then
        build_frontend
    else
        print_warning "Skipping frontend build as requested."
    fi

    # Step 4: Run Flask API
    print_status "Setup complete! Now starting the Flask API server..."
    run_flask_api
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
