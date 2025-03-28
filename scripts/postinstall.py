# postinstall.py
import nltk
import textblob.download_corpora
import spacy

print("📦 Downloading NLTK resources...")
nltk.download("punkt")

print("🧠 Downloading TextBlob corpora...")
textblob.download_corpora.download_all()

print("💬 Downloading spaCy English model...")
spacy.cli.download("en_core_web_sm")

print("✅ All NLP models downloaded!")
