from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from emotion_enhancer import EmotionEnhancer  # Your existing enhancement module

# Initialize Emotion Enhancer and VADER
enhancer = EmotionEnhancer()
vader = SentimentIntensityAnalyzer()

# Load FinBERT
finbert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
finbert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
finbert_model.eval()

# FinBERT label order: 0-neutral, 1-positive, 2-negative
finbert_labels = ['neutral', 'positive', 'negative']

def finbert_sentiment(text):
    inputs = finbert_tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = finbert_model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)[0]
    return {label: round(probs[i].item(), 3) for i, label in enumerate(finbert_labels)}

def full_vader_analysis(text):
    # Get enhanced metrics from EmotionEnhancer
    enhanced = enhancer.enhance_emotion_analysis(text)
    # Get base VADER sentiment scores
    vader_scores = vader.polarity_scores(text)
    return {
        "polarity": enhanced["polarity"],
        "stress_score": enhanced["stress_score"],
        "relaxation_score": enhanced["relaxation_score"],
        "casual_score": enhanced["casual_score"],
        "formal_score": enhanced["formal_score"],
        "sarcasm_score": enhanced["sarcasm_score"],
        "vader_pos": vader_scores["pos"],
        "vader_neu": vader_scores["neu"],
        "vader_neg": vader_scores["neg"]
    }

# Test texts
texts = [
    "Jeff,Jacques Craig will draw up a release.  What is the status on the quote from Wade?  Phillip",
    "Let me know when you get the quotes from Pauline.  I am expecting to pay something in the $3,000 to $5,000 range.  I would like to see the quotes and a description of the work to be done.  It is my understanding that some rock will be removed and replaced with siding.  If they are getting quotes to put up new rock then we will need to clarify.Jacques is ready to drop in a dollar amount on the release.  If the negotiations stall, it seems like I need to go ahead and cut off the utilities.  Hopefully things will go smoothly.Phillip",
    "Bruce,Just a reminder, this Wednesday (Dec 13) is the Associate PRC meeting in which Sally will be representing Cheryl Ingstad.  She really needs your input in order to properly represent Cheryl.  Please email information to her ASAP or call Sally with information Tuesday between 9:00 - 9:30 AM (3:00 - 3:30 PM London time).Thanks for your assistance,Patti x39106",
    "Yes, you are nuts!  I can't believe that you already have so many gingerbread houses made.  The cookie exchange was fun - fudge is definitely the easy route on that one.  I will get the recipe from home tonight and will e:mail it to you tomorrow.  -Sally ",
    "Credit cards that is! - I just requested another $50 Macy's GC - this is still the best reward that they have (we have another 2,500 points already).  Also, I straightened up the deal with AT&T Long distance and they are going to correct the bill to $33.23 and starting with the next bill we are supposed to get 120 minutes a month of free long distance so talk up.  Also, two other things - I checked BofA and the Negril pulse came through as $142.09 and also I was looking at the AT&T credit card and it had a charge for $117.50 from Chi's cakes and more.  I guess that is just the charge for the cake but wanted to make sure the it wasn't for the cake stands.  Since we are both big rich types you want to go to dinner tonight?  Let me know.Love Hubby"
]

results = []

def compare_models(texts):
    for text in texts:
        vader_result = full_vader_analysis(text)
        finbert_scores = finbert_sentiment(text)

        results.append({
            "text": text,
            "vader_polarity": vader_result["polarity"],
            "vader_stress": vader_result["stress_score"],
            "vader_relaxation": vader_result["relaxation_score"],
            "vader_casual": vader_result["casual_score"],
            "vader_formal": vader_result["formal_score"],
            "vader_sarcasm": vader_result["sarcasm_score"],
            "vader_pos": vader_result["vader_pos"],
            "vader_neu": vader_result["vader_neu"],
            "vader_neg": vader_result["vader_neg"],
            "finbert_positive": finbert_scores["positive"],
            "finbert_neutral": finbert_scores["neutral"],
            "finbert_negative": finbert_scores["negative"],
        })

        print(f"\nText: {text}")
        print("VADER (enhanced + base) result:", vader_result)
        print("FinBERT scores:", finbert_scores)

def analyze_results():
    df = pd.DataFrame(results)

    print("\n=== Basic Stats ===")
    print(df.describe())

    print("\n=== Correlation ===")
    print(df[['vader_polarity', 'vader_pos', 'vader_neu', 'vader_neg',
              'finbert_positive', 'finbert_neutral', 'finbert_negative']].corr())

    # Assign simple labels
    df['text_label'] = [f"Text {i+1}" for i in range(len(df))]

    # Reshape for plotting
    melted_df = pd.melt(
        df,
        id_vars=["text_label"],
        value_vars=[
            "vader_pos", "vader_neu", "vader_neg",
            "finbert_positive", "finbert_neutral", "finbert_negative"
        ],
        var_name="model_sentiment",
        value_name="score"
    )

    # Map to better labels
    label_map = {
        "vader_pos": "VADER Positive",
        "vader_neu": "VADER Neutral",
        "vader_neg": "VADER Negative",
        "finbert_positive": "FinBERT Positive",
        "finbert_neutral": "FinBERT Neutral",
        "finbert_negative": "FinBERT Negative"
    }
    color_map = {
        "VADER Positive": "#2ca02c",   # green
        "VADER Neutral": "#1f77b4",    # blue
        "VADER Negative": "#d62728",   # red
        "FinBERT Positive": "#98df8a", # light green
        "FinBERT Neutral": "#aec7e8",  # light blue
        "FinBERT Negative": "#ff9896"  # light red/pink
    }

    melted_df["Sentiment Type"] = melted_df["model_sentiment"].map(label_map)

    plt.figure(figsize=(12, max(5, len(df) * 1)))
    sns.barplot(
        data=melted_df,
        x="score",
        y="text_label",
        hue="Sentiment Type",
        palette=color_map,
        dodge=True
    )

    plt.title("Sentiment Comparison: VADER vs FinBERT", fontsize=16)
    plt.xlabel("Sentiment Score")
    plt.ylabel("Text Sample")
    plt.legend(title="Model + Sentiment", loc="upper right", frameon=True, borderpad=1)
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


# Run comparison and analysis
if __name__ == "__main__":
    compare_models(texts)
    analyze_results()
