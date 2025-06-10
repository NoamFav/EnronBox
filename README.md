<div align="center">

# 📬 EnronClassifier

[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Tauri](https://img.shields.io/badge/Tauri-Latest-purple.svg)](https://tauri.app/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-blue.svg)](https://www.docker.com/)
[![Transformers](https://img.shields.io/badge/🤗_Transformers-Latest-yellow.svg)](https://huggingface.co/transformers/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Latest-blue.svg)](https://www.typescriptlang.org/)

<img src="apps/enron_classifier/src-tauri/icons/icon.png" width="250" alt="EnronClassifier Logo"/>

A powerful desktop and web application for classifying, summarizing, and analyzing emotion in Enron emails. Built with React, Flask API, and Tauri for cross-platform support, featuring advanced transformer models with GPU acceleration.

[Quick Start](#-quick-start) •
[Features](#-features) •
[Architecture](#-architecture) •
[Development](#-development)

</div>

---

## 📋 Overview

Welcome to **EnronClassifier**, a sophisticated email analysis application! Built with cutting-edge transformer models and NLP techniques, it provides comprehensive email classification, summarization, and emotion analysis capabilities through an elegant web and desktop interface. Whether you're a data scientist, researcher, or NLP enthusiast, this tool offers powerful insights into the Enron email dataset!

<div align="center">
  <img src="docs/screenshots.png" width="600" alt="EnronClassifier Screenshot"/>
</div>

---

## 🚀 Features

<div style="display: flex; flex-wrap: wrap;">

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🧠 Advanced Email Classification</h3>
<p>Uses state-of-the-art transformer models including BART and DistilBERT for zero-shot classification with 10 comprehensive categories.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>📄 Smart Summarization</h3>
<p>Extractive summarization of lengthy emails using advanced NLP libraries (NLTK, spaCy, Sumy).</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🧠 Emotion Analysis</h3>
<p>Detects emotional tone and offers phrasing suggestions to enhance communication.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>👤 User Selection</h3>
<p>Select and analyze emails from specific Enron employees in the dataset.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>⚡ GPU Acceleration</h3>
<p>Full CUDA support for high-performance inference, with limited MPS support for Apple Silicon.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>💻 Cross-Platform</h3>
<p>Available as both a web application and desktop app via Tauri framework.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🤖 AI Response Generation</h3>
<p>Intelligent email response generation powered by Ollama integration.</p>
</div>

</div>

---

## 🏷️ Classification Categories

The system classifies emails into 10 comprehensive categories:

| Category | Description |
|----------|-------------|
| **Strategic Planning** | Long-term business strategy, corporate planning, acquisitions |
| **Daily Operations** | Day-to-day operations, routine tasks, procedures |
| **Financial** | Budget, accounting, financial reports, expenses |
| **Legal & Compliance** | Legal matters, regulatory compliance, contracts |
| **Client & External** | External communications, client relations, partnerships |
| **HR & Personnel** | Human resources, hiring, employee matters |
| **Meetings & Events** | Meeting scheduling, event planning, appointments |
| **Urgent & Critical** | Time-sensitive, emergency, critical issues |
| **Personal & Informal** | Personal communications, informal chats, non-work related |
| **Technical & IT** | Technical issues, IT support, system problems |

---

## 🚀 Quick Start

<details open>
<summary><b>Prerequisites</b></summary>

Before diving into the email analysis, ensure your system meets these requirements:

| Requirement                 | Version | Notes                                                         |
| --------------------------- | ------- | ------------------------------------------------------------- |
| **Node.js & npm**           | v18+    | [Download Node.js](https://nodejs.org/)                       |
| **Docker & Docker Compose** | Latest  | [Get Docker](https://www.docker.com/products/docker-desktop/) (Windows only) |
| **Rust toolchain**          | Latest  | Required for Tauri builds                                     |
| **Python**                  | 3.10+   | For local development of Flask API                            |
| **Ollama**                  | Latest  | [Install Ollama](https://ollama.com) for AI response generation |

**Hardware Acceleration Support:**
- **CUDA GPU**: Full acceleration support for NVIDIA GPUs
- **Apple Silicon (M1/M2)**: Limited MPS acceleration (native Flask recommended)
- **CPU**: Fallback support for all systems

</details>

---

## 🖥️ Platform-Specific Setup

### 🪟 Windows Setup

<details>
<summary><b>Windows Installation (Docker-based)</b></summary>

For Windows users, we use Docker for the complete backend setup:

```bash
# 1. Download and extract the Enron dataset
./bin/download_enron.cmd

# 2. Generate the SQLite database
./bin/generate_db.cmd

# 3. Start the Flask API with Docker
docker compose up --build

# 4. In a new terminal, run the desktop application
npm --prefix ./apps/enron_classifier run tauri dev
```

Or for the web version:
```bash
# Run the web version
npm --prefix ./apps/enron_classifier run dev
```

</details>

---

### 🐧 Unix Setup (Linux, macOS, WSL)

<details open>
<summary><b>One-Command Setup (Recommended)</b></summary>

For Unix-based systems (Linux, macOS, WSL), use our streamlined setup script:

```bash
# Complete setup - downloads data, builds database, frontend, and starts API
./bin/enron_classifier.sh
```

**That's it!** The script will:
1. Download and extract the Enron dataset
2. Generate the SQLite database from scratch
3. Install frontend dependencies and build the application
4. Start the Flask API server
5. Launch the desktop application

</details>

<details>
<summary><b>Advanced Usage Options</b></summary>

The `enron_classifier.sh` script supports various options for different workflows:

```bash
# Show help and available options
./bin/enron_classifier.sh --help

# Only download and extract the Enron dataset
./bin/enron_classifier.sh --download-only

# Only generate the database (requires dataset to be downloaded)
./bin/enron_classifier.sh --db-only

# Only build the frontend application
./bin/enron_classifier.sh --frontend-only

# Only run the Flask API server
./bin/enron_classifier.sh --api-only

# Run complete setup but skip frontend building
./bin/enron_classifier.sh --skip-frontend
```

**Usage Examples:**
```bash
# Fresh installation
./bin/enron_classifier.sh

# Update database only
./bin/enron_classifier.sh --db-only

# Development: rebuild frontend only
./bin/enron_classifier.sh --frontend-only

# Run just the API for development
./bin/enron_classifier.sh --api-only
```

</details>

---

## 🤖 Ollama Setup

<details>
<summary><b>AI Response Generation Setup</b></summary>

For AI-powered email response generation, you need to install and configure Ollama:

```bash
# 1. Install Ollama from https://ollama.com

# 2. Pull a recommended model (choose one)
ollama pull llama3.2:3b        # Lightweight, fast responses
ollama pull llama3.1:8b        # Balanced performance
ollama pull codellama:7b       # For technical emails

# 3. Verify installation
ollama list
```

The application will automatically detect available Ollama models and use them for intelligent email response generation.

</details>

---

## 🛠️ Architecture

<details open>
<summary><b>System Architecture</b></summary>

```
┌──────────────┐    HTTP    ┌───────────────┐    AI Models    ┌─────────────┐
│   Frontend   │──────────▶│  Flask API     │◀───────────────│   Ollama    │
│ (React +     │◀──────────│  (Advanced NLP │                 │  (Optional) │
│  Tauri)      │           │   Pipeline)    │                 └─────────────┘
└──────────────┘           └───────────────┘
                                ▲
                                │
                           ┌──────────┐
                           │ SQLite   │
                           │ (enron.db)│
                           └──────────┘
```

The system uses a modern architecture with three main components:

1. **Frontend**: React-based UI with Tauri integration for desktop deployment
2. **Flask API**: Python backend with transformer models for advanced ML and NLP processing
3. **Ollama Integration**: Optional AI service for intelligent response generation

### Advanced ML Pipeline

The classification system uses state-of-the-art transformer models:

- **Sentence Transformer**: `all-MiniLM-L6-v2` for semantic embeddings
- **Zero-shot Classification**: `facebook/bart-base` for flexible email categorization
- **Tokenization**: `distilbert-base-uncased` for efficient text processing
- **Ollama Models**: Various LLMs for response generation (llama3.2, codellama, etc.)

**Device Optimization:**
- Automatic GPU detection and optimization
- CUDA support for NVIDIA GPUs
- MPS support for Apple Silicon (with fallback handling)
- Intelligent CPU fallback for unsupported configurations

</details>

<details>
<summary><b>API Endpoints</b></summary>

The Flask API exposes these endpoints for frontend integration:

| Route                     | Method | Description                      |
| ------------------------- | ------ | -------------------------------- |
| `/classify`               | POST   | Classify email content using transformers |
| `/summarize`              | POST   | Summarize email text             |
| `/emotion-enhance`        | POST   | Analyze & enhance emotional tone |
| `/users`                  | GET    | List available Enron users       |
| `/users/<user_id>/emails` | GET    | Fetch emails for a specific user |
| `/ner`                    | POST   | Named entity recognition         |
| `/respond`                | POST   | AI-powered email response generation |

</details>

---

## 💻 Development

<details>
<summary><b>Clone & Setup</b></summary>

```bash
# Clone the repository
git clone https://github.com/NoamFav/NLP_project.git
cd NLP_project

# For Unix systems (Linux, macOS, WSL) - One command setup
./bin/enron_classifier.sh

# For Windows - Manual setup
./bin/download_enron.cmd
./bin/generate_db.cmd
docker compose up --build
```

</details>

<details>
<summary><b>Frontend Development</b></summary>

Start the React app in development mode:

```bash
# Desktop application
npm --prefix ./apps/enron_classifier run tauri dev

# Web application
npm --prefix ./apps/enron_classifier run dev
```

The UI is built with:

- Vite + React 18
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- React Router DOM for navigation

</details>

<details>
<summary><b>Backend Development</b></summary>

### Using the Setup Script (Unix)

```bash
# Run only the API for development
./bin/enron_classifier.sh --api-only
```

### Using Docker (Windows/Cross-platform)

```bash
docker compose up --build
```

### Manual Setup

```bash
cd apps/flask_api
pip install -r requirements.txt
python -m app.server
```

</details>

---

## 📁 Project Structure

```
NLP_project/
├── apps/
│   ├── flask_api/            # Flask backend & Dockerfile
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routes/       # API endpoints
│   │   │   ├── services/     # ML/NLP services
│   │   │   │   ├── enron_classifier.py  # Advanced transformer pipeline
│   │   │   │   ├── emotion_enhancer.py
│   │   │   │   ├── summarizer.py
│   │   │   │   ├── responder.py         # AI response generation
│   │   │   │   ├── ollama_service.py    # Ollama integration
│   │   │   │   └── ner_engine.py
│   │   │   ├── tests/        # Evaluation scripts
│   │   │   └── ui/           # CLI interface
│   │   ├── data/
│   │   │   └── enron.db      # Generated Enron dataset
│   │   ├── models/           # Trained ML models
│   │   └── requirements.txt  # Python dependencies
│   ├── enron_classifier/     # Frontend code
│   │   ├── src/
│   │   │   ├── components/   # React components
│   │   │   ├── contexts/     # React contexts
│   │   │   ├── hooks/        # Custom hooks
│   │   │   ├── pages/        # Application pages
│   │   │   └── utils/        # Utility functions
│   │   └── src-tauri/        # Tauri configuration
│   └── SQLite_db/            # Database generation
│       └── generate_db.py    # Database creation script
├── bin/
│   ├── enron_classifier.sh   # 🆕 Unix one-command setup
│   ├── download_enron.*      # Data download scripts
│   ├── generate_db.*         # Database generation scripts
│   └── flask-api.sh          # Native Flask runner
├── docker-compose.yml        # Service definitions
└── README.md
```

---

## ⚡ Performance Notes

### GPU Acceleration

- **CUDA**: Full support with automatic device detection
- **Apple Silicon (MPS)**: Limited support due to Hugging Face compatibility issues
- **Docker on macOS**: Does not support MPS - use native setup for better performance

### Recommended Setup by Platform

| Platform | Setup Command | Performance |
|----------|---------------|-------------|
| **Linux with NVIDIA GPU** | `./bin/enron_classifier.sh` | Excellent (Full CUDA) |
| **Windows with NVIDIA GPU** | Docker setup | Excellent (Full CUDA) |
| **macOS (Intel)** | `./bin/enron_classifier.sh` | Good (CPU) |
| **macOS (Apple Silicon)** | `./bin/enron_classifier.sh` | Good (Limited MPS) |
| **WSL** | `./bin/enron_classifier.sh` | Good (CPU/CUDA if configured) |

---

## 🎯 Available Scripts

<details>
<summary><b>Setup Scripts</b></summary>

| Command | Platform | Description |
| ------- | -------- | ----------- |
| `./bin/enron_classifier.sh` | Unix (Linux, macOS, WSL) | Complete one-command setup |
| `./bin/enron_classifier.sh --help` | Unix | Show all available options |
| `./bin/download_enron.cmd` | Windows | Download Enron dataset |
| `./bin/generate_db.cmd` | Windows | Generate SQLite database |
| `docker compose up --build` | All | Run Flask API with Docker |

</details>

<details>
<summary><b>Frontend Scripts</b></summary>

| Command               | Description                            |
| --------------------- | -------------------------------------- |
| `npm run dev`         | Start web app in development mode      |
| `npm run build`       | Build frontend for production          |
| `npm run preview`     | Preview production build locally       |
| `npm run tauri dev`   | Start Tauri desktop app                |
| `npm run tauri build` | Build desktop application              |
| `npm run lint`        | Run ESLint checks                      |

</details>

---

## 🤝 Contributing

<details>
<summary><b>Contribution Guidelines</b></summary>

We welcome contributions to make EnronClassifier even better! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the code style guidelines.

</details>

---

## 🔧 Troubleshooting

<details>
<summary><b>Common Issues</b></summary>

**Setup Script Issues (Unix):**
```bash
# Make sure the script is executable
chmod +x ./bin/enron_classifier.sh

# Run with verbose output
bash -x ./bin/enron_classifier.sh
```

**Docker Issues (Windows):**
```bash
# Ensure Docker is running and try rebuilding
docker compose down
docker compose up --build --force-recreate
```

**Ollama Connection Issues:**
```bash
# Verify Ollama is running
ollama list

# Test connection
curl http://localhost:11434/api/tags
```

**Node.js/NPM Issues:**
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

</details>

---

## 👤 Contributors

<div align="center">

| Contributor            | Role           | Focus Area                        |
| ---------------------- | -------------- | --------------------------------- |
| **Project Lead**       | Lead Developer | Architecture, ML Integration      |
| **Backend Developer**  | Developer      | Flask API, Transformer Models    |
| **Frontend Developer** | Developer      | React, Tauri Integration          |
| **ML Engineer**        | Data Scientist | Advanced NLP Pipeline, GPU Optimization |
| **UX Designer**        | Designer       | User Interface, Experience Design |

</div>

> 💌 Special thanks to the Enron corpus, Hugging Face, Ollama, and the open-source community for the foundational tools.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

---

<div align="center">

### 📧 Happy Email Analysis with AI! 📧

</div>