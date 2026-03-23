# 📬 EnronBox

<div align="center">

<img src="https://img.shields.io/badge/react-18+-61DAFB.svg?style=for-the-badge&logo=react" alt="React">
<img src="https://img.shields.io/badge/flask-3.1-black.svg?style=for-the-badge&logo=flask" alt="Flask">
<img src="https://img.shields.io/badge/tauri-latest-24C8DB.svg?style=for-the-badge&logo=tauri" alt="Tauri">
<img src="https://img.shields.io/badge/docker-compatible-2496ED.svg?style=for-the-badge&logo=docker" alt="Docker">
<img src="https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge" alt="License">

**AI-powered email analysis platform for the Enron dataset**

[Quick Start](#quick-start) · [Features](#features) · [Architecture](#architecture)

</div>

---

EnronBox combines transformer-based NLP with a cross-platform desktop UI to classify, summarize, and analyze emails from the Enron corpus — with GPU acceleration, Ollama-powered responses, and emotion detection.

> Initial label generation can take ~10 minutes per 10k emails on CPU. Training on 100k emails takes ~20 minutes on modern hardware.

---

## Quick Start

**Unix / macOS / WSL:**
```bash
./bin/enron_classifier.sh
```

**Windows:**
```bash
./bin/download_enron.cmd
./bin/generate_db.cmd
docker compose up --build
npm --prefix ./apps/enron_classifier run tauri dev
```

---

## Features

- Zero-shot classification into 10 categories (BART transformer)
- Extractive summarization (NLTK, spaCy, Sumy)
- Emotion and sentiment detection with confidence scores
- AI response generation via Ollama (Llama, Mistral, CodeLlama)
- GPU acceleration — CUDA, Apple Silicon MPS, CPU fallback
- Desktop app via Tauri and web interface via React

---

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, JavaScript, Tailwind CSS |
| Desktop | Tauri, Rust |
| API | Flask 3.1, Python 3.10+ |
| ML/NLP | Transformers, BART, DistilBERT, NLTK, spaCy |
| Database | SQLite |
| AI | Ollama, Llama, Mistral |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/classify` | POST | Email classification |
| `/summarize` | POST | Text summarization |
| `/emotion-enhance` | POST | Emotion analysis |
| `/respond` | POST | AI response generation |
| `/users` | GET | List Enron users |
| `/users/<id>/emails` | GET | User's emails |

---

## Retrain the Model

```bash
curl -X POST http://localhost:5050/api/classify/train \
  -H "Content-Type: application/json" \
  -d '{"enron_dir": "../SQLite_db/enron.db", "max_emails": 500000}'
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit and open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
Made with ❤️ by <a href="https://github.com/NoamFav">NoamFav</a>
</div>
