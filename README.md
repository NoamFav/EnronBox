# 📬 Enron Email Intelligence

A powerful terminal-based email classification and analysis tool powered by machine learning and NLP, built on the Enron email dataset. The application offers a rich terminal UI using the `rich` library, featuring category classification, emotion analysis, keyword extraction, and smart commands.

---

## 🚀 Features

### 🧠 AI-Powered Email Classification (`enron_classifier.py`)

- **Hybrid Classifier**:

  - Combines a TF-IDF + Random Forest pipeline with a numerical model using handcrafted features.
  - Final prediction made via probabilistic fusion of both models for higher accuracy.

- **Category Detection**:

  - Classifies emails into categories such as `Work`, `Personal`, `Spam`, `Travel`, `Social`, etc.
  - Labels inferred from folder structure and intelligently expanded using heuristics.

- **Advanced Feature Engineering**:

  - Text length features for subject and body.
  - Sentiment analysis using TextBlob (polarity & subjectivity).
  - Urgency scoring based on keywords like “urgent”, “immediately”, etc.
  - Email metadata extraction: attachment presence, number of recipients, CCs, BCCs.
  - Business language and external sender detection.

- **Model Evaluation**:
  - Confusion matrix, accuracy score, and a full classification report using scikit-learn.

---

### 🖥️ Terminal UI Shell (`ui/enron_shell.py`)

- Built with `PromptToolkit` and `rich` for a clean, interactive shell experience.
- Custom prompt, colors, and emoji-enhanced output.
- Keyboard-friendly Vim-style commands prefixed with `:`:
  - `:browse` — browse and load emails via `fzf`
  - `:analyze` — run classification, sentiment, emotion, urgency prediction
  - `:response` — generate an auto-response
  - `:user` — view email statistics for any user via `fzf`
  - `:entities` — extract named entities (people 👤, orgs 🏢, dates 📅)
  - `:summary` — generate an extractive summary
  - `:clear` — reset the screen
  - `:help` — list all commands
  - `:quit` — exit the shell

---

### 📄 Summarization Module (`summarizer/summarizer.py`)

- Generates short, extractive summaries from long email bodies.
- Uses the `Sumy` library and various algorithms like LSA to preserve meaning.
- Integrated into `:summarize` command and auto-used on long emails.

---

### 🧍 Entity Extraction (`ner/extractor.py`)

- Performs Named Entity Recognition using spaCy.
- Extracts key elements such as:
  - 👤 Person names
  - 🏢 Organizations
  - 📅 Dates and temporal expressions
- Displayed automatically after classification to enhance context understanding.

---

### ✉️ Auto Reply Generator (`response/responder.py`)

- Uses sentiment, urgency, and category predictions to generate templated responses.
- Context-aware formatting (e.g. "Thanks for your positive feedback about..." vs "We regret the inconvenience caused...").
- Supports categories: `Work`, `Personal`, `Default`, and has special formatting for urgent emails.

---

### 🧠 Emotion & Urgency Enhancer (`emotion_enhancer.py`)

- Augments TextBlob with additional emotion metrics:
  - Stress vs Relaxation heuristics
  - Improved tone detection for edge cases
- Better guides the auto-reply module and helps highlight emotionally charged content.

---

### 🎛️ CLI Input Mode (Under Development)

- Allows entering custom emails directly into the shell.
- Useful for testing classifier, reply system, or NER without loading Enron data.
- Will support JSON or free-text entry formats.

---

## 🏁 Running the Shell

```bash
# Unix/macOS
./run.sh --max_emails 5000

# Windows
run.bat --max_emails 5000
```

- **Note**: Always run from the project root (paths are relative for now)
- **Tip**: Keep `max_emails` under 5000 for faster startup during dev — the full dataset is over 500k emails!

---

## 📦 Setup Instructions

### ▶️ Installation (Cross-platform)

- Use the Makefile (Linux/macOS) or `install.bat` (Windows) to install dependencies and download models.

#### **Linux/macOS**:

```bash
make install
```

#### **Windows**:

```cmd
install.bat
```

- This installs dependencies from `requirements.txt` and runs:
  - `python -m nltk.downloader punkt`
  - `python -m textblob.download_corpora`
  - `python -m spacy download en_core_web_sm`

---

## 📥 Dataset Download

Use the platform-specific scripts in `bin/`:

```bash
# macOS/Linux
bash bin/download_enron.sh

# Windows
bin\download_enron.cmd
```

---

## 📁 Project Structure

```
├── bin/                 # Scripts: dataset download (sh/cmd)
├── data/                # Preprocessed data (optional)
├── docs/                # Documentation and diagrams
├── maildir/             # Enron dataset folder (after extraction)
├── results/             # Output files and evaluations
├── scripts/             # Postinstall and misc helpers
├── src/                 # Source code
│   ├── ui/              # Terminal shell UI
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

## 👤 Contributors

- **Noam Favier** – Project Lead, UI Integration, ML Core
- **Remi** – Email Summarization
- **Jiang** – Named Entity Recognition
- **Giorgos** – Auto-Reply Templates
- **David** – Sentiment Enhancer
- **Esteban** – Dataset Cleanup / Metadata
- **Octavian** – Manual Tester / Custom Email Input

> 💌 Special thanks to the Enron corpus and the open NLP community for the foundational tools.
