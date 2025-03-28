import re  # Import the existing summarization libraries
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import os


def download_nltk_resources():
    """
    Ensure NLTK resources are downloaded
    """
    # List of resources to download
    resources = ["punkt", "punkt_tab"]  # Tokenizer  # Additional tokenizer resource

    # Download each resource
    for resource in resources:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            print(f"Downloading NLTK resource: {resource}")
            nltk.download(resource, quiet=True)


download_nltk_resources()


class EmailSummarizer:
    def __init__(self):
        # Ensure punkt is downloaded
        download_nltk_resources()

    def extract_email_body(self, email_text):
        """
        Extracts only the actual email message and removes metadata like headers, CC/BCC, and signatures.
        """
        # Remove common email headers
        email_text = re.sub(
            r"^(Message-ID|From|To|Subject|Date|Cc|Bcc|Mime-Version|Content-Type|Content-Transfer-Encoding|X-[\w-]+):.*$",
            "",
            email_text,
            flags=re.MULTILINE,
        )

        # Remove Enron-specific metadata (folder, origin, file name, etc.)
        email_text = re.sub(
            r"X-Folder:.*|X-Origin:.*|X-FileName:.*", "", email_text, flags=re.MULTILINE
        )

        # Remove email forwarding/reply metadata (quoted text, "---Original Message---", etc.)
        email_text = re.sub(
            r"(-{2,}|={2,})\s*(Original Message|Forwarded by).*",
            "",
            email_text,
            flags=re.DOTALL,
        )

        # Remove repeated email addresses (from CC, BCC, etc.)
        email_text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w{2,3}", "", email_text)

        # Remove excessive new lines
        email_text = re.sub(r"\n\s*\n+", "\n\n", email_text).strip()

        return email_text

    def summarize_email(self, email_text, num_sentences=3):
        """
        Summarize the email using LSA (Latent Semantic Analysis) method

        Args:
            email_text (str): Full email text
            num_sentences (int, optional): Number of sentences in summary. Defaults to 3.

        Returns:
            str: Summarized email text
        """
        try:
            # Clean the email body first
            cleaned_text = self.extract_email_body(email_text)

            # Parse and summarize
            parser = PlaintextParser.from_string(cleaned_text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, num_sentences)

            return "\n".join(str(sentence) for sentence in summary)
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Unable to generate summary."
