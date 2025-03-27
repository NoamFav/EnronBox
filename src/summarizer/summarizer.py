import os
import subprocess
import sys
import pandas as pd
import random
import re

# ✅ FUNCTION TO INSTALL MISSING LIBRARIES AUTOMATICALLY
def install_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"📌 INSTALLING MISSING PACKAGE: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)

# ✅ CHECK AND INSTALL REQUIRED LIBRARIES
install_missing("sumy")
install_missing("nltk")

# ✅ IMPORT LIBRARIES AFTER INSTALLATION
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

# ✅ DOWNLOAD NLTK TOKENIZER IF MISSING
nltk.download("punkt", quiet=True)

# ✅ DEFINE PATH TO EMAIL DATASET
csv_file = r"C:\yourfilepath\emails.csv"

# ✅ FUNCTION TO CLEAN EMAIL BODY (REMOVE HEADERS, METADATA, SIGNATURES)
def extract_email_body(email_text):
    """
    Extracts only the actual email message and removes metadata like headers, CC/BCC, and signatures.
    """
    # Remove common email headers
    email_text = re.sub(
        r"^(Message-ID|From|To|Subject|Date|Cc|Bcc|Mime-Version|Content-Type|Content-Transfer-Encoding|X-[\w-]+):.*$", 
        "", email_text, flags=re.MULTILINE
    )

    # Remove Enron-specific metadata (folder, origin, file name, etc.)
    email_text = re.sub(r"X-Folder:.*|X-Origin:.*|X-FileName:.*", "", email_text, flags=re.MULTILINE)

    # Remove email forwarding/reply metadata (quoted text, "---Original Message---", etc.)
    email_text = re.sub(r"(-{2,}|={2,})\s*(Original Message|Forwarded by).*", "", email_text, flags=re.DOTALL)

    # Remove repeated email addresses (from CC, BCC, etc.)
    email_text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w{2,3}", "", email_text)

    # Remove excessive new lines
    email_text = re.sub(r"\n\s*\n+", "\n\n", email_text).strip()

    return email_text

# ✅ FUNCTION TO SUMMARIZE EMAIL AUTOMATICALLY (NO USER INPUT)
def summarize_email(email_text):
    print("\n📌 SUMMARIZING EMAIL...\n")
    parser = PlaintextParser.from_string(email_text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # Default: 3 sentences
    return "\n".join(str(sentence) for sentence in summary)

# ✅ ATTEMPT TO LOAD EMAIL DATA OR USE A DEFAULT EMAIL
if os.path.exists(csv_file):
    try:
        print("📂 LOADING EMAIL DATA FROM CSV FILE...")
        df = pd.read_csv(csv_file)

        if "message" in df.columns and not df.empty:
            # ✅ PICK A RANDOM EMAIL AND CLEAN IT
            random_email = df.sample(n=1)["message"].values[0]
            cleaned_email = extract_email_body(random_email)
        else:
            raise ValueError("❌ ERROR: CSV FILE IS EMPTY OR MISSING 'message' COLUMN")
    except Exception as e:
        print(f"❌ ERROR LOADING CSV FILE: {e}")
        cleaned_email = None
else:
    print("❌ CSV FILE NOT FOUND. USING A DEFAULT EMAIL INSTEAD.")
    cleaned_email = None

# ✅ DEFAULT EMAIL IF CSV FILE FAILS
if not cleaned_email:
    cleaned_email = """  
    Dear Team,  

    I hope this email finds you well. I wanted to provide an update on our project progress. We have completed the initial research phase and identified key areas of improvement. The next step will be to implement the recommended changes and test their effectiveness. Additionally, I’d like to remind everyone that our next team meeting is scheduled for Friday at 3 PM.  

    This is a fake email to test the summarization.  
    Let me know if you have any questions.  
    How are you guys?
    Best regards,  
    Remi
    """

print("\n🔹 EMAIL TO BE SUMMARIZED 🔹\n")
print(cleaned_email[:1000])  # Print first 1000 characters for preview

# ✅ GENERATE SUMMARY AUTOMATICALLY
summary = summarize_email(cleaned_email)

print("\n🔹 EMAIL SUMMARY 🔹\n")
print(summary)

print("\n✅ DONE! EMAIL SUMMARIZATION COMPLETED SUCCESSFULLY 🎉")
