<div align="center">

# 📬 Enron Email Intelligence

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Latest-orange.svg)](https://scikit-learn.org/)
[![Rich](https://img.shields.io/badge/Rich-Latest-purple.svg)](https://github.com/Textualize/rich)
[![TextBlob](https://img.shields.io/badge/TextBlob-Latest-green.svg)](https://textblob.readthedocs.io/)
[![spaCy](https://img.shields.io/badge/spaCy-Latest-teal.svg)](https://spacy.io/)

<div align="center">

# 📬 EnronClassifier

[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Tauri](https://img.shields.io/badge/Tauri-Latest-purple.svg)](https://tauri.app/)
[![Docker](https://img.shields.io/badge/Docker-Compatible-blue.svg)](https://www.docker.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Latest-orange.svg)](https://scikit-learn.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Latest-blue.svg)](https://www.typescriptlang.org/)

<img src="src/assets/logo.png" width="250" alt="EnronClassifier Logo"/>

A powerful desktop and web application for classifying, summarizing, and analyzing emotion in Enron emails. Built with React, Flask API, and Tauri for cross-platform support.

[Quick Start](#-quick-start) •
[Features](#-features) •
[Architecture](#-architecture) •
[Development](#-development)

</div>

---

## 📋 Overview

Welcome to **EnronClassifier**, a sophisticated email analysis application! Built with advanced machine learning and NLP techniques, it provides comprehensive email classification, summarization, and emotion analysis capabilities through an elegant web and desktop interface. Whether you're a data scientist, researcher, or NLP enthusiast, this tool offers powerful insights into the Enron email dataset!

<div align="center">
  <img src="docs/images/app_screenshot.png" width="600" alt="EnronClassifier Screenshot"/>
</div>

---

## 🚀 Features

<div style="display: flex; flex-wrap: wrap;">

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🧠 Email Classification</h3>
<p>Uses machine learning to categorize emails with high accuracy using a Python ML pipeline.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>📄 Smart Summarization</h3>
<p>Extractive summarization of lengthy emails using NLP libraries (NLTK, spaCy, Sumy).</p>
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
<h3>🔄 Agent Daemon</h3>
<p>Background Go service for asynchronous tasks and seamless integrations.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>💻 Cross-Platform</h3>
<p>Available as both a web application and desktop app via Tauri framework.</p>
</div>

</div>

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
| **Go**                      | 1.20+   | For agent-daemon development                                  |

</details>

<details open>
<summary><b>Docker Setup (Backend)</b></summary>

Launch the backend services quickly with Docker Compose:

```bash
# Start the Flask API and Agent Daemon
docker-compose up --build
```

This will start:

- **Flask API** on port 5050
- **Agent Daemon** working in the background

Both services will connect to the pre-loaded Enron SQLite database.

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
│ (React +     │◀──────────│  (apps/flask_api)│
│  Tauri)      │           └───────────────┘
└──────────────┘                ▲
                                │
                                │
                           ┌──────────┐
                           │ SQLite   │
                           │ (enron.db)│
                           └──────────┘
                                ▲
                                │
                           ┌──────────┐
                           │Agent     │
                           │Daemon    │
                           └──────────┘
```

The system uses a modern architecture with three main components:

1. **Frontend**: React-based UI with Tauri integration for desktop deployment
2. **Flask API**: Python backend for ML and NLP processing
3. **Agent Daemon**: Go service for background tasks and database maintenance

</details>

<details>
<summary><b>API Endpoints</b></summary>

The Flask API exposes these endpoints for frontend integration:

| Route                     | Method | Description                      |
| ------------------------- | ------ | -------------------------------- |
| `/classify`               | POST   | Classify email content           |
| `/summarize`              | POST   | Summarize email text             |
| `/emotion-enhance`        | POST   | Analyze & enhance emotional tone |
| `/users`                  | GET    | List available Enron users       |
| `/users/<user_id>/emails` | GET    | Fetch emails for a specific user |

</details>

---

## 💻 Development

<details>
<summary><b>Clone & Setup</b></summary>

```bash
# Clone the repository
git clone https://github.com/your-org/EnronClassifier.git
cd EnronClassifier

# Install dependencies
npm install

# Set up Python environment
pip install -r requirements.txt
```

</details>

<details>
<summary><b>Environment Variables</b></summary>

Create a `.env` file in the project root:

```dotenv
# For Flask API
db_path=./apps/SQLite_db/enron.db
PORT=5050
```

</details>

<details>
<summary><b>Frontend Development</b></summary>

Start the React app in development mode:

```bash
npm run dev
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

Run the Flask API without Docker:

```bash
cd apps/flask_api
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port 5050
```

The Go agent daemon can be run separately:

```bash
cd apps/go_agents/agent-daemon
go run main.go
```

</details>

---

## 📁 Project Structure

```
EnronClassifier/
├── apps/
│   ├── flask_api/            # Flask backend & Dockerfile
│   │   ├── app.py
│   │   ├── models/
│   │   └── services/
│   ├── go_agents/            # Go agent-daemon service
│   │   └── agent-daemon/
│   └── enron_classifier/     # Frontend code
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   └── services/
│       └── src-tauri/        # Tauri configuration
├── SQLite_db/
│   └── enron.db              # Pre-loaded Enron dataset
├── package.json
├── requirements.txt          # Python dependencies
└── docker-compose.yml        # Service definitions
```

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
| `npm run predeploy`   | Build before deploying to GitHub Pages |
| `npm run deploy`      | Deploy to GitHub Pages                 |

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
| **Backend Developer**  | Developer      | Flask API, Classification         |
| **Frontend Developer** | Developer      | React, Tauri Integration          |
| **Go Developer**       | Developer      | Agent Daemon                      |
| **ML Engineer**        | Data Scientist | ML Models, NLP Pipeline           |
| **UX Designer**        | Designer       | User Interface, Experience Design |

</div>

> 💌 Special thanks to the Enron corpus and the open-source community for the foundational tools.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 📧 Happy Email Analysis! 📧

</div>
