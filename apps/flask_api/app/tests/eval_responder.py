from app.services.responder import Responder
from sklearn.metrics import bleu_score

# assume you have a CSV of (thread_history, human_reply)
import pandas as pd

df = pd.read_csv("data/email_replies.csv")

responder = Responder()
bleu_scores = []

for _, row in df.iterrows():
    auto = responder.generate_reply(
        history=row.thread_history, to_address=row.from_address
    )
    reference = [row.human_reply.split()]
    hypothesis = auto.split()
    bleu = bleu_score.sentence_bleu(reference, hypothesis)
    bleu_scores.append(bleu)

print("Avg BLEU:", sum(bleu_scores) / len(bleu_scores))
