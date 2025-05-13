# eval_summarization.py
from app.services.summarizer import Summarizer
from rouge import Rouge
import json

# Load a JSON of { thread: "...", summary: "..." }
with open("data/email_summaries.json") as f:
    examples = json.load(f)

summ = Summarizer()
rouge = Rouge()

scores = []
for ex in examples:
    auto_sum = summ.summarize(ex["thread"])
    sc = rouge.get_scores(auto_sum, ex["summary"])[0]
    scores.append(sc)

# average over all examples
avg = {metric: sum(d[metric] for d in scores) / len(scores) for metric in scores[0]}
print("Average ROUGE:", avg)
