<div align="center">

# 📬 Enron Email Intelligence

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Latest-orange.svg)](https://scikit-learn.org/)
[![Rich](https://img.shields.io/badge/Rich-Latest-purple.svg)](https://github.com/Textualize/rich)
[![TextBlob](https://img.shields.io/badge/TextBlob-Latest-green.svg)](https://textblob.readthedocs.io/)
[![spaCy](https://img.shields.io/badge/spaCy-Latest-teal.svg)](https://spacy.io/)

<img src="src/ui/assets/logo.png" width="250" alt="Enron Email Intelligence Logo"/>

A powerful terminal-based email classification and analysis tool powered by machine learning and NLP, built on the Enron email dataset. The application offers a rich terminal UI using the `rich` library, featuring category classification, emotion analysis, keyword extraction, and smart commands.

[Installation](#-setup-instructions) • 
[Features](#-features) • 
[Running the Shell](#-running-the-shell) • 
[Project Structure](#-project-structure)

</div>

---

## 📋 Overview

Welcome to **Enron Email Intelligence**, a sophisticated email analysis toolkit! Built with advanced machine learning and NLP techniques, it provides comprehensive email classification, sentiment analysis, and intelligent processing capabilities through an elegant terminal interface. Whether you're a data scientist, email administrator, or NLP enthusiast, this tool offers powerful insights into email communications!

<div align="center">
  <img src="docs/images/terminal_ui_screenshot.png" width="600" alt="Enron Email Intelligence Terminal UI"/>
</div>

---

## 🚀 Features

<div style="display: flex; flex-wrap: wrap;">

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🧠 AI-Powered Classification</h3>
<p>Advanced hybrid classifier combining TF-IDF with Random Forest and custom numerical features for highly accurate email categorization.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🖥️ Rich Terminal UI</h3>
<p>Elegant, interactive terminal interface with custom prompts, colors, and emoji-enhanced output for a delightful user experience.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>📄 Smart Summarization</h3>
<p>Extract key information from lengthy emails using advanced algorithms that preserve context and meaning.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🧍 Entity Recognition</h3>
<p>Automatically identify and extract people, organizations, dates, and locations from email content to enhance context understanding.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>✉️ Auto-Reply Generation</h3>
<p>Create contextually appropriate email responses based on sentiment, urgency, and category predictions.</p>
</div>

<div style="flex: 1; min-width: 250px; padding: 10px;">
<h3>🧠 Emotion Analysis</h3>
<p>Advanced sentiment and emotion detection to identify stress, urgency, and tone in communications.</p>
</div>

</div>

---

## 📦 Setup Instructions

<details open>
<summary><b>Installation Requirements</b></summary>

Before diving into the email analysis, ensure your system meets these requirements:

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.8+ | [Download Python](https://www.python.org/downloads/) |
| **pip** | Latest | Included with Python |
| **Memory** | 4GB+ RAM | 8GB+ recommended for full dataset |
| **Storage** | 1GB | For dataset and dependencies |
| **OS** | Cross-platform | Windows, macOS, Linux compatible |

</details>

<details open>
<summary><b>Quick Installation</b></summary>

Follow these simple steps to set up the application:

### **Linux/macOS**:

```bash
# Clone the repository (if using git)
git clone https://github.com/NoamFav/NLP_project.git
cd NLP_project

# Install dependencies
make install
```

### **Windows**:

```cmd
# Clone the repository (if using git)
git clone https://github.com/NoamFav/NLP_project.git
cd NLP_project

# Install dependencies
install.bat
```

The installer automatically handles all dependencies and downloads required NLP models.

</details>

<details>
<summary><b>Dataset Download</b></summary>

Use the platform-specific scripts to download and extract the Enron email dataset:

**macOS/Linux**:
```bash
bash bin/download_enron.sh
```

**Windows**:
```cmd
bin\download_enron.cmd
```

This will download, extract, and prepare the dataset for analysis.

</details>

---

## 🏁 Running the Shell

<details open>
<summary><b>Launch Instructions</b></summary>

Start the interactive shell with these commands:

```bash
# Unix/macOS
./run.sh --max_emails 5000

# Windows
run.bat --max_emails 5000
```

**Tips for Optimal Performance**:
- Keep `max_emails` under 5000 for faster startup during development
- Always run from the project root directory
- For production use, increase the email limit for more comprehensive analysis

</details>

<details>
<summary><b>Shell Commands</b></summary>

Navigate the application using these Vim-style commands:

| Command | Description | Usage |
|---------|-------------|-------|
| `:browse` | Browse and load emails | `:browse [folder]` |
| `:analyze` | Run full analysis on current email | `:analyze` |
| `:response` | Generate auto-response | `:response` |
| `:user` | View email statistics for any user | `:user [email/name]` |
| `:entities` | Extract named entities | `:entities` |
| `:summary` | Generate email summary | `:summary` |
| `:clear` | Reset the screen | `:clear` |
| `:help` | List all commands | `:help` |
| `:quit` | Exit the shell | `:quit` |

</details>

<div align="center">
  <img src="docs/images/command_showcase.png" width="600" alt="Terminal Command Showcase"/>
</div>

---

## 🛠️ Technical Details

<details>
<summary><b>Classification Details</b></summary>

The email classifier employs a sophisticated hybrid approach:

- **Text Pipeline**:
  - TF-IDF vectorization with n-gram features
  - Random Forest classifier with optimized hyperparameters
  - Stop word removal and lemmatization

- **Numerical Features**:
  - Text length metrics (subject, body)
  - Sentiment analysis (polarity, subjectivity)
  - Urgency scoring based on keyword frequency
  - Email metadata extraction (recipients, CCs, attachments)
  - Business language detection

- **Fusion Strategy**:
  - Probabilistic combination of text and numerical predictions
  - Confidence thresholds for improved precision

</details>

<details>
<summary><b>Entity Extraction Process</b></summary>

Named Entity Recognition is performed using spaCy:

1. Pre-processing to clean and normalize text
2. Entity detection for:
   - People (👤 names, positions)
   - Organizations (🏢 companies, departments)
   - Dates and times (📅 scheduling information)
   - Locations (🌎 places, addresses)
3. Post-processing to remove duplicates and improve accuracy
4. Rich visualization in the terminal interface

</details>

---

## 📁 Project Structure

```
enron-email-intelligence/
├── bin/                 # Scripts: dataset download (sh/cmd)
├── data/                # Preprocessed data (optional)
├── docs/                # Documentation and diagrams
│   └── images/          # Screenshots and visual aids
├── maildir/             # Enron dataset folder (after extraction)
├── results/             # Output files and evaluations
├── scripts/             # Postinstall and misc helpers
├── src/                 # Source code
│   ├── ui/              # Terminal shell UI
│   │   └── assets/      # UI resources and icons
│   ├── ner/             # Named Entity Recognition
│   ├── response/        # Auto-response engine
│   ├── summarizer/      # Email summarizer
│   ├── emotion_enhancer.py
│   ├── enron_classifier.py
│   └── main.py
├── install.bat          # Windows installer
├── Makefile             # Linux/macOS installer
├── postinstall.py       # Common setup tasks
├── README.md            # Project overview
└── requirements.txt     # Python dependencies
```

---

## 🎯 Planned Features

<table>
<tr>
<td width="33%">
<h3>🌐 Web Interface</h3>
<p>Browser-based UI for easier access and visualization capabilities.</p>
</td>
<td width="33%">
<h3>📊 Advanced Analytics</h3>
<p>Statistical insights and communication pattern discovery across emails.</p>
</td>
<td width="33%">
<h3>🔄 Custom Email Input</h3>
<p>Analyze your own emails beyond the Enron dataset.</p>
</td>
</tr>
<tr>
<td width="33%">
<h3>🧪 Improved Models</h3>
<p>Enhanced classification using transformer-based approaches.</p>
</td>
<td width="33%">
<h3>📱 Export Capabilities</h3>
<p>Save analyses in various formats (PDF, CSV, JSON).</p>
</td>
<td width="33%">
<h3>🔌 API Integration</h3>
<p>Connect with email services for real-time analysis.</p>
</td>
</tr>
</table>

---

## 👤 Contributors

<div align="center">

| Contributor | Role | Focus Area |
|-------------|------|------------|
| **Noam Favier** | Project Lead | UI Integration, ML Core |
| **Remi** | Developer | Email Summarization |
| **Jiang** | Developer | Named Entity Recognition |
| **Giorgos** | Developer | Auto-Reply Templates |
| **David** | Developer | Sentiment Enhancer |
| **Esteban** | Data Scientist | Dataset Cleanup / Metadata |
| **Octavian** | Tester | Manual Testing / Custom Email Input |

</div>

> 💌 Special thanks to the Enron corpus and the open NLP community for the foundational tools.

---

## 🤝 Contributing

We welcome contributions to make Enron Email Intelligence even better! Whether it's adding new features, fixing bugs, or improving documentation, your help is appreciated.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the code style guidelines.

---

<div align="center">

### 📧 Happy Email Analysis! 📧

</div>
