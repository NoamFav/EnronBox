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
| **Docker & Docker Compose** | Latest  | [Get Docker](https://www.docker.com/products/docker-desktop/) |
| **Rust toolchain**          | Latest  | Required for Tauri builds                                     |
| **Python**                  | 3.10+   | For local development of Flask API                            |

**Hardware Acceleration Support:**
- **CUDA GPU**: Full acceleration support for NVIDIA GPUs
- **Apple Silicon (M1/M2)**: Limited MPS acceleration (native Flask recommended)
- **CPU**: Fallback support for all systems

</details>

<details open>
<summary><b>Backend Setup</b></summary>

### Docker Setup (Recommended for Linux/Windows)

Launch the backend services quickly with Docker Compose:

```bash
# Start the Flask API
docker compose up --build
```

This will start the **Flask API** on port 5050 with the pre-loaded Enron SQLite database.

### Native Flask Setup (Recommended for macOS)

For optimal performance on macOS with Apple Silicon, run Flask natively to leverage MPS acceleration:

```bash
# Run the Flask API setup script (handles dependencies and execution)
./bin/flask-api.sh
```

> **Note for macOS users**: Docker doesn't support MPS acceleration, so running Flask natively provides significantly better performance on Apple Silicon devices.

</details>

<details open>
<summary><b>Running the Application</b></summary>

### Desktop Application (Development)

```bash
# Run the Tauri desktop app in development mode
npm --prefix ./apps/enron_classifier run tauri dev
```

### Desktop Application (Production Build)

```bash
# Build the desktop application installers
npm --prefix ./apps/enron_classifier run tauri build
```

Installers will be available in `apps/enron_classifier/src-tauri/target/release/bundle/`.

### Web Application

```bash
# Run the web version in development mode
npm --prefix ./apps/enron_classifier run dev
```

Access the web app at http://localhost:5173

</details>

---

## 🛠️ Architecture

<details open>
<summary><b>System Architecture</b></summary>

```
┌──────────────┐    HTTP    ┌───────────────┐
│   Frontend   │──────────▶│  Flask API     │
│ (React +     │◀──────────│  (Advanced NLP │
│  Tauri)      │           │   Pipeline)    │
└──────────────┘           └───────────────┘
                                ▲
                                │
                           ┌──────────┐
                           │ SQLite   │
                           │ (enron.db)│
                           └──────────┘
```

The system uses a modern architecture with two main components:

1. **Frontend**: React-based UI with Tauri integration for desktop deployment
2. **Flask API**: Python backend with transformer models for advanced ML and NLP processing

### Advanced ML Pipeline

The classification system uses state-of-the-art transformer models:

- **Sentence Transformer**: `all-MiniLM-L6-v2` for semantic embeddings
- **Zero-shot Classification**: `facebook/bart-base` for flexible email categorization
- **Tokenization**: `distilbert-base-uncased` for efficient text processing

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

# Install dependencies
npm --prefix ./apps/enron_classifier install
```

</details>

<details>
<summary><b>Frontend Development</b></summary>

Start the React app in development mode:

```bash
npm --prefix ./apps/enron_classifier run tauri dev
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

### Using Docker (Linux/Windows)

```bash
docker compose up --build
```

### Using Native Flask (macOS recommended)

```bash
# Setup and run Flask API
./bin/flask-api.sh
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
│   │   │   │   └── ner_engine.py
│   │   │   ├── tests/        # Evaluation scripts
│   │   │   └── ui/           # CLI interface
│   │   ├── data/
│   │   │   └── enron.db      # Pre-loaded Enron dataset
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
│   └── SQLite_db/            # Database initialization
├── bin/
│   ├── flask-api.sh          # Native Flask runner for macOS
│   └── download_enron.*      # Data download scripts
├── docker-compose.yml        # Service definitions
└── README.md
```

---

## ⚡ Performance Notes

### GPU Acceleration

- **CUDA**: Full support with automatic device detection
- **Apple Silicon (MPS)**: Limited support due to Hugging Face compatibility issues
- **Docker on macOS**: Does not support MPS - use native Flask for better performance

### Recommended Setup by Platform

| Platform | Backend Setup | Performance |
|----------|---------------|-------------|
| **Linux with NVIDIA GPU** | Docker | Excellent (Full CUDA) |
| **Windows with NVIDIA GPU** | Docker | Excellent (Full CUDA) |
| **macOS (Intel)** | Docker or Native | Good (CPU) |
| **macOS (Apple Silicon)** | Native Flask | Good (Limited MPS) |
| **Any other** | Docker or Native | Fair (CPU fallback) |

---

## 🎯 Available Scripts

<details>
<summary><b>Main Package Scripts</b></summary>

| Command               | Description                            |
| --------------------- | -------------------------------------- |
| `npm run dev`         | Start frontend in development mode     |
| `npm run build`       | Build frontend for production          |
| `npm run preview`     | Preview production build locally       |
| `npm run tauri dev`   | Start Tauri dev environment            |
| `npm run tauri build` | Build desktop application              |
| `npm run lint`        | Run ESLint checks                      |

</details>

<details>
<summary><b>Backend Scripts</b></summary>

| Command                    | Description                            |
| -------------------------- | -------------------------------------- |
| `./bin/flask-api.sh`       | Run Flask API natively (macOS recommended) |
| `docker compose up --build` | Run Flask API in Docker               |

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

> 💌 Special thanks to the Enron corpus, Hugging Face, and the open-source community for the foundational tools.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

---

<div align="center">

### 📧 Happy Email Analysis with AI! 📧

</div>