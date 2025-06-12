<div align="center">

# 📬 EnronClassifier

[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tauri](https://img.shields.io/badge/Tauri-Latest-24C8DB.svg?style=for-the-badge&logo=tauri&logoColor=white)](https://tauri.app/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![HuggingFace](https://img.shields.io/badge/🤗_Transformers-Latest-FFD21E.svg?style=for-the-badge)](https://huggingface.co/transformers/)
[![JavaScript](https://img.shields.io/badge/JavaScript-Latest-3178C6.svg?style=for-the-badge&logo=JavaScript&logoColor=white)](https://www.JavaScriptlang.org/)

<img src="apps/enron_classifier/src-tauri/icons/icon.png" width="200" alt="EnronClassifier Logo" style="border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);"/>

### 🚀 Advanced Email Intelligence Platform

**Transform email analysis with AI-powered classification, summarization, and emotion detection**

<p align="center">
  <a href="#-quick-start"><kbd> <br> 🚀 Quick Start <br> </kbd></a>&nbsp;&nbsp;
  <a href="#-features"><kbd> <br> ✨ Features <br> </kbd></a>&nbsp;&nbsp;
  <a href="#-architecture"><kbd> <br> 🏗️ Architecture <br> </kbd></a>&nbsp;&nbsp;
  <a href="#-development"><kbd> <br> 💻 Development <br> </kbd></a>
</p>

</div>

> **🎯 Built for researchers, data scientists, and NLP enthusiasts** — Leverage cutting-edge transformer models and advanced NLP techniques to unlock insights from the Enron email dataset with GPU-accelerated performance.

---

## 🌟 What is EnronClassifier?

**EnronClassifier** is a sophisticated email analysis platform that combines the power of modern transformer models with an intuitive cross-platform interface. Whether you're conducting research, analyzing communication patterns, or exploring NLP techniques, our application provides comprehensive tools for email classification, summarization, and emotion analysis.

<div align="center">
  <img src="docs/screenshots.png" width="800" alt="EnronClassifier Interface" style="border-radius: 12px; box-shadow: 0 12px 48px rgba(0,0,0,0.1); margin: 20px 0;"/>
</div>

---

## ✨ Key Features

⚠️ Note: The initial label generation step can take time (e.g. ~10 minutes per 10k emails on CPU), but it runs automatically as part of the training process — no manual labeling required!

<table>
<tr>
<td width="50%">

### 🧠 **Intelligent Classification**

- **10 comprehensive categories** for precise email sorting
- **Zero-shot classification** using BART transformer
- **Semantic understanding** with sentence transformers
- **Multi-label support** for complex emails

</td>
<td width="50%">

### 📄 **Smart Summarization**

- **Extractive summarization** using NLTK, spaCy, Sumy
- **Key phrase extraction** for quick insights
- **Configurable length** based on your needs
- **Context preservation** for accurate summaries

</td>
</tr>
<tr>
<td width="50%">

### 🎭 **Emotion Analysis**

- **Sentiment detection** with confidence scores
- **Tone analysis** for communication insights
- **Enhancement suggestions** for better phrasing
- **Emotional context** understanding

</td>
<td width="50%">

### 🤖 **AI Response Generation**

- **Ollama integration** for intelligent replies
- **Context-aware responses** based on email content
- **Multiple LLM options** (Llama, CodeLlama, Mistral)
- **Customizable tone** and style

</td>
</tr>
<tr>
<td width="50%">

### ⚡ **Performance Optimized**

- **GPU acceleration** with full CUDA support
- **Apple Silicon (MPS)** compatibility
- **Intelligent fallback** to CPU when needed
- **Efficient caching** for faster processing

</td>
<td width="50%">

### 💻 **Cross-Platform**

- **Desktop app** via Tauri framework
- **Web interface** for browser-based usage
- **Docker support** for easy deployment
- **Unix & Windows** compatibility

</td>
</tr>
</table>

---

## 🏷️ Classification System

Our advanced classification system categorizes emails into **10 distinct categories** using state-of-the-art transformer models:

<div align="center">

| 🎯 Category                | 📝 Description                                       | 🔍 Examples                                   |
| -------------------------- | ---------------------------------------------------- | --------------------------------------------- |
| **🎯 Strategic Planning**  | Long-term strategy, acquisitions, corporate planning | "Q4 merger discussion", "5-year growth plan"  |
| **⚙️ Daily Operations**    | Routine tasks, operational procedures                | "Daily status update", "Process changes"      |
| **💰 Financial**           | Budget, accounting, expense reports                  | "Monthly P&L", "Budget approval"              |
| **⚖️ Legal & Compliance**  | Legal matters, regulatory compliance                 | "Contract review", "Compliance audit"         |
| **🤝 Client & External**   | External communications, partnerships                | "Client meeting", "Vendor negotiation"        |
| **👥 HR & Personnel**      | Human resources, hiring matters                      | "New hire onboarding", "Performance review"   |
| **🗓️ Meetings & Events**   | Scheduling, event planning                           | "Board meeting agenda", "Conference planning" |
| **🚨 Urgent & Critical**   | Time-sensitive, emergency issues                     | "System outage", "Urgent approval needed"     |
| **💬 Personal & Informal** | Personal communications, informal chats              | "Lunch plans", "Weekend discussion"           |
| **🔧 Technical & IT**      | Technical support, system issues                     | "Server maintenance", "Software bug report"   |

</div>

---

## 🚀 Quick Start Guide

### 📋 Prerequisites

<div align="center">

| 🛠️ Tool           | 📌 Version | 📝 Notes                                                      |
| ----------------- | ---------- | ------------------------------------------------------------- |
| **Node.js & npm** | `v18+`     | [Download here](https://nodejs.org/)                          |
| **Docker**        | `Latest`   | [Get Docker](https://www.docker.com/products/docker-desktop/) |
| **Rust**          | `Latest`   | Required for Tauri builds                                     |
| **Python**        | `3.10+`    | For local Flask development                                   |
| **Ollama**        | `Latest`   | **Required** - [Install Ollama](https://ollama.com)           |

</div>

### 🎯 One-Command Setup

<table>
<tr>
<td width="50%" align="center">

### 🐧 **Unix Systems**

_Linux, macOS, WSL_

```bash
# Complete setup in one command
./bin/enron_classifier.sh
```

**That's it!** ✨ The script handles everything:

- 📥 Downloads Enron dataset
- 🗄️ Builds SQLite database
- 🎨 Installs frontend dependencies
- 🤖 Sets up Ollama models
- 🚀 Starts Flask API
- 💻 Launches desktop app

</td>
<td width="50%" align="center">

### 🪟 **Windows**

_Docker-based setup_

```bash
# 1. Download dataset
./bin/download_enron.cmd

# 2. Generate database
./bin/generate_db.cmd

# 3. Start services
docker compose up --build

# 4. Launch desktop app
npm --prefix ./apps/enron_classifier run tauri dev
```

</td>
</tr>
</table>

### 🤖 Ollama Setup

<details>
<summary><b>AI Response Generation Setup</b></summary>

For AI-powered email response generation, you need to install and configure Ollama:

```bash
# 1. Install Ollama from https://ollama.com

# 2. Pull a recommended model (choose one)
ollama pull llama3.2:3b        # Lightweight, fast responses
ollama pull llama3.1:8b        # Balanced performance
ollama pull codellama:7b       # For technical emails
ollama pull mistral            # Default model

# 3. Verify installation
ollama list
```

By default, the shell script `./bin/enron_classifier.sh` checks whether the default model (configured in the app) is installed using `ollama list`. If the model is missing, the script automatically pulls it using `ollama pull`.

You can change the default model by editing the file:

```javascript
// apps/enron_classifier/src/config.js

// API configuration
export const API_URL = 'http://localhost:5050/api';

// Timeout configuration (in milliseconds)
export const API_TIMEOUT = 240000; // 4 minutes

// Model configuration
export const DEFAULT_MODEL = 'mistral';
export const DEFAULT_TEMPERATURE = 0.7;
```

⚠️ **Important:**
The application uses only the configured default model defined in `config.js` for response generation. It does not automatically select other models even if they're installed.

</details>

---

## 🏗️ Architecture Overview

<div align="center">

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React + JavaScript UI]
        B[Tauri Desktop Wrapper]
        C[Web Application]
    end

    subgraph "API Layer"
        D[Flask REST API]
        E[Advanced NLP Pipeline]
        F[Transformer Models]
    end

    subgraph "Data Layer"
        G[SQLite Database]
        H[Enron Email Dataset]
    end

    subgraph "AI Services"
        I[Ollama Server]
        J[LLM Models]
    end

    A --> D
    B --> A
    C --> A
    D --> E
    E --> F
    D --> G
    G --> H
    D --> I
    I --> J

    style A fill:#61DAFB,stroke:#21325B,color:#000
    style D fill:#000000,stroke:#FFFFFF,color:#fff
    style F fill:#FFD21E,stroke:#FF6B35,color:#000
    style I fill:#00D4AA,stroke:#007A5E,color:#000
```

</div>

### 🔧 Technology Stack

<div align="center">

| Layer           | Technologies                                      | Purpose                            |
| --------------- | ------------------------------------------------- | ---------------------------------- |
| **🎨 Frontend** | React 18, JavaScript, Tailwind CSS, Framer Motion | Modern, responsive user interface  |
| **🖥️ Desktop**  | Tauri, Rust                                       | Cross-platform desktop application |
| **🔗 API**      | Flask 3.1, Python 3.10+                           | RESTful backend services           |
| **🧠 ML/NLP**   | Transformers, BART, DistilBERT, NLTK, spaCy       | Advanced language processing       |
| **🗄️ Database** | SQLite                                            | Efficient email data storage       |
| **🤖 AI**       | Ollama, Llama models, Mistral                     | Intelligent response generation    |

</div>

---

## 🛠️ Development Setup

### 📁 Project Structure

```
NLP_project/
├── 📱 apps/
│   ├── 🐍 flask_api/              # Backend API
│   │   ├── app/
│   │   │   ├── 🛣️ routes/         # API endpoints
│   │   │   ├── 🔧 services/       # ML/NLP services
│   │   │   │   ├── 🧠 enron_classifier.py
│   │   │   │   ├── 🎭 emotion_enhancer.py
│   │   │   │   ├── 📄 summarizer.py
│   │   │   │   ├── 🤖 responder.py
│   │   │   │   └── 🏷️ ner_engine.py
│   │   │   └── 🧪 tests/
│   │   └── 📊 models/
│   ├── ⚛️ enron_classifier/       # Frontend React app
│   │   ├── src/
│   │   │   ├── 🧩 components/
│   │   │   ├── 🔄 contexts/
│   │   │   ├── 🪝 hooks/
│   │   │   └── 📱 pages/
│   │   └── 🦀 src-tauri/         # Tauri config
│   └── 🗄️ SQLite_db/             # Database generation
├── 📜 bin/                       # Setup scripts
├── 🐳 docker-compose.yml
└── 📖 README.md
```

### 🚀 Development Commands

<div align="center">

| Command                                     | Description                | Platform |
| ------------------------------------------- | -------------------------- | -------- |
| `./bin/enron_classifier.sh`                 | 🎯 Complete setup          | Unix     |
| `./bin/enron_classifier.sh --api-only`      | 🔧 API development         | Unix     |
| `./bin/enron_classifier.sh --frontend-only` | 🎨 Frontend development    | Unix     |
| `docker compose up --build`                 | 🐳 Docker development      | All      |
| `npm run tauri dev`                         | 🖥️ Desktop app development | All      |
| `npm run dev`                               | 🌐 Web app development     | All      |

</div>

### 🔗 API Endpoints

<div align="center">

| 🛣️ Endpoint          | 📝 Method | 🎯 Purpose             | 📊 Input      |
| -------------------- | --------- | ---------------------- | ------------- |
| `/classify`          | `POST`    | Email classification   | Email text    |
| `/summarize`         | `POST`    | Text summarization     | Email content |
| `/emotion-enhance`   | `POST`    | Emotion analysis       | Email text    |
| `/respond`           | `POST`    | AI response generation | Email context |
| `/users`             | `GET`     | List Enron users       | None          |
| `/users/<id>/emails` | `GET`     | User's emails          | User ID       |

</div>

---

## ⚡ Performance & Optimization

### 🎯 Hardware Acceleration

<div align="center">

| 🖥️ Platform                  | 🚀 Acceleration | 📈 Performance       | 🛠️ Setup Command            |
| ---------------------------- | --------------- | -------------------- | --------------------------- |
| **🐧 Linux + NVIDIA**        | Full CUDA       | ⭐⭐⭐⭐⭐ Excellent | `./bin/enron_classifier.sh` |
| **🪟 Windows + NVIDIA**      | Full CUDA       | ⭐⭐⭐⭐⭐ Excellent | Docker setup                |
| **🍎 macOS (Apple Silicon)** | Limited MPS     | ⭐⭐⭐⭐ Good        | `./bin/enron_classifier.sh` |
| **🍎 macOS (Intel)**         | CPU only        | ⭐⭐⭐ Good          | `./bin/enron_classifier.sh` |
| **🐧 WSL**                   | CPU/CUDA        | ⭐⭐⭐⭐ Good        | `./bin/enron_classifier.sh` |

</div>

### 💡 Performance Tips

- **🚀 GPU Acceleration**: Use NVIDIA GPUs for best performance
- **🍎 Apple Silicon**: Native setup recommended over Docker
- **💾 Memory**: 8GB+ RAM recommended for large datasets
- **🔄 Caching**: Models are cached after first load

### 📊 Model Training Note

The classifier **uses a fast, transformer-based zero-shot labeling system** to assign initial labels to each email (based on BART embeddings or sentence embeddings + cosine similarity).  
This means even the very first training round **generates labels automatically**, but for best accuracy you may want to retrain on more data.

By default, the model is trained on a **100k email sample** (~20 minutes on modern hardware).  
For best results, we recommend training on the **full dataset** (~500k emails), which may take around **1.5–2 hours** depending on your CPU or GPU.

You can retrain easily using the built-in API:

```bash
curl -i -X POST http://localhost:5050/api/classify/train \
 -H "Content-Type: application/json" \
 -d '{"enron_dir": "../SQLite_db/enron.db", "max_emails": 500000}'

```

or, for Docker users:

```bash
curl -i -X POST http://localhost:5050/api/classify/train \
-H "Content-Type: application/json" \
-d '{"enron_dir": "app/data/enron.db", "max_emails": 500000}'
```

⚠️ Note: The initial label generation step can take time (e.g. ~10 minutes per 10k emails on CPU), but it runs automatically as part of the training process — no manual labeling required!

## 🧪 Running the Enron Email Classifier Test Suite

This test suite evaluates the **Enron Email Classifier** on a **small subset of emails** to ensure the training pipeline, model creation, and classification process work correctly.

### 📝 What the Test Does:

- Loads **3,000 emails** from the Enron dataset.
- Uses the **zero-shot labeler** (embedding-based or BART) to generate initial labels for these emails.
- Trains a **fresh model from scratch** on this small dataset using an ensemble classifier.
- Evaluates performance on a 600-email test set and generates:
  - A **confusion matrix** heatmap
  - A **detailed classification report**
  - A **CSV** file with per-email predictions and confidences.
- Saves all results in the `test_results/` directory.

### ⚡ Why Such a Small Dataset?

- Training on the full dataset (~500k emails) would take **hours**, even on a powerful machine.
- This test uses **only 3,000 emails** to keep the test fast and manageable—roughly **10–15 seconds** to run.
- Performance on this small test set is **expected to be low (accuracy ~10–20%)** due to the limited data.

### 🚀 How to Run It:

```bash
python3 -m app.tests.classification_test
```

**Note**: The test always trains a new model from scratch on the 3,000-email sample.
For production, train the model on a larger dataset (100k+ emails) using the training endpoint (recommended).

## 🛠️ Troubleshooting

<details>
<summary><b>🔧 Common Issues & Solutions</b></summary>

### 🐧 Unix Setup Issues

```bash
# Make script executable
chmod +x ./bin/enron_classifier.sh

# Run with debug output
bash -x ./bin/enron_classifier.sh
```

### 🐳 Docker Issues

```bash
# Reset Docker environment
docker compose down --volumes
docker compose up --build --force-recreate
```

### 🤖 Ollama Connection Issues

```bash
# Check Ollama status
ollama list
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve
```

### 📦 Node.js Issues

```bash
# Clear and reinstall dependencies
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

</details>

---

## 🤝 Contributing

<div align="center">

### 🌟 We welcome contributions!

[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

</div>

**How to contribute:**

1. 🍴 **Fork** the repository
2. 🌿 **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. ✨ **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. 🚀 **Push** to the branch (`git push origin feature/amazing-feature`)
5. 🎯 **Open** a Pull Request

**Contribution areas:**

- 🧠 ML model improvements
- 🎨 UI/UX enhancements
- 📚 Documentation updates
- 🧪 Test coverage expansion
- 🐛 Bug fixes

---

## 👥 Team

<div align="center">

| Role                      | Focus                      | Expertise                      |
| ------------------------- | -------------------------- | ------------------------------ |
| **🚀 Lead Developer**     | Architecture & Integration | Full-stack, ML Pipeline        |
| **🧠 ML Engineer**        | NLP & AI Models            | Transformers, GPU Optimization |
| **🎨 Frontend Developer** | UI/UX & React              | JavaScript, Modern Web         |
| **🐍 Backend Developer**  | API & Services             | Flask, Python, Databases       |
| **📊 Data Scientist**     | Analytics & Insights       | Statistics, Visualization      |

</div>

---

## 📜 License

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE.md) file for details.

</div>

---

## 🙏 Acknowledgments

<div align="center">

**Built with ❤️ and powered by:**

[![Hugging Face](https://img.shields.io/badge/🤗-Hugging%20Face-FFD21E?style=for-the-badge)](https://huggingface.co/)
[![Ollama](https://img.shields.io/badge/🦙-Ollama-00D4AA?style=for-the-badge)](https://ollama.com/)
[![Enron Corpus](https://img.shields.io/badge/📧-Enron%20Dataset-FF6B35?style=for-the-badge)](https://www.cs.cmu.edu/~enron/)

_Special thanks to the open-source community and research institutions that make advanced NLP accessible to everyone._

</div>

---

<div align="center">

### 🎉 Ready to revolutionize email analysis?

<a href="#-quick-start"><kbd> <br> 🚀 Get Started Now <br> </kbd></a>

**📧 Transform emails into insights with AI! 📧**

</div>
