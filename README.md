📬 Enron Email Intelligence

A powerful terminal-based email classification and analysis tool powered by machine learning and NLP, built on the Enron email dataset. The application offers a rich terminal UI using the `rich` library, featuring category classification, emotion analysis, keyword extraction, and smart commands.

---

## 🚀 Features Implemented

### ✅ AI Backend (`enron_classifier.py`)

- **Email Preprocessing**: HTML cleaning, tokenization, stopword removal, lemmatization.
- **Feature Extraction**:
  - Subject/body length
  - Sentiment & subjectivity with TextBlob
  - Urgency detection via keywords
  - Metadata (attachments, recipient count, etc.)
  - Business phrase detection & external sender flag
- **Dual Model Training**:
  - TF-IDF + Random Forest for text
  - Numerical model with handcrafted features
  - Probabilistic fusion of both for prediction
- **Confusion matrix output**
- **Model evaluation & classification report**

### ✅ Terminal UI (`ui/enron_shell.py`)

- **Interactive Shell**: Uses `PromptToolkit` for an interactive prompt with commands.
- **Command System** (prefixed with `:` like in Vim):
  - `:browse` — Browse the email set
  - `:analyze` — Run prediction & sentiment/emotion analysis on selected email
  - `:user` — View stats about users in the dataset
  - `:help` — Display list of commands
- **Beautiful Output**:
  - Rich progress bars during loading
  - Panels for messages and reports
  - Tables with classification metrics and stats

### ✅ Dataset Loader

- Optimized email loading with per-user and global progress bars
- Supports limiting the number of emails (`--max_emails`) for faster testing
- Automatically categorizes emails into 7 possible categories based on folder names

---

## 🧩 Planned Features by Teammates

Each feature will plug into `main.py` and be callable from the shell via dedicated commands (or auto-analysis).

### 🧾 Remi – **Summarization**

- Create extractive summaries from email threads.
- `summarizer/summarizer.py`
- `summarize_thread(body: str) -> str`

### 🧍‍♂️ Jiang – **Named Entity Recognition**

- Extract names, orgs, dates from the email body using spaCy.
- `ner/extractor.py`
- `extract_entities(body: str) -> dict`

### 🤖 Giorgos – **Auto-Reply Generation**

- Generate template-based responses based on the category/sentiment.
- `response/responder.py`
- `generate_reply(email: dict, prediction: dict) -> str`

### 🧠 David – **Sentiment/Urgency Enhancer**

- Improve sarcasm detection, or enrich the urgency heuristics.
- Patch `enron_classifier.py` or create a helper script.

### 📚 Esteban – **Dataset Labeling Support**

- Clean and enrich dataset labels
- Support thread-based metadata (e.g., `thread_id`, `depth`)
- Work within `data/` or a helper script

### 🧪 Octavian – **Manual Testing & CLI Input**

- Build a helper to test with user-inputted or custom sample emails.
- Could be a CLI input loop or sample menu.

---

## 🏁 Running the Shell

```bash
python3 src/main.py --max_emails 5000
```

- **Note**: Always run from the project root (paths are relative for now)
- **Tip**: Keep `max_emails` under 5000 for faster startup during dev -- the full dataset is 500k emails!

---

## 🧠 Future

- Add `:summarize`, `:entities`, `:reply`, etc. commands to use teammate features
- Add support for multi-thread conversation analysis
- Refactor `main.py` as entry point for pipeline & UI combo

---

## 👤 Contributors

- **Noam Favier** – Project Lead, UI Integration, ML Core
- **Remi** – Email Summarization
- **Jiang** – Named Entity Recognition
- **Giorgos** – Auto-Reply Templates
- **David** – Sentiment Enhancer
- **Esteban** – Dataset Cleanup / Metadata
- **Octavian** – Manual Tester / Custom Email Input

> Special thanks to the Enron corpus and the open NLP community for the foundational tools 💌
