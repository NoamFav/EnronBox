import time
from app.services.enron_classifier import EnronEmailClassifier
from app.services.summarizer import Summarizer

clf = EnronEmailClassifier("/app/models")
summ = Summarizer()

emails = load_test_emails()  # list of raw text

# Baseline: manual
start = time.time()
for e in emails:
    _ = human_label(e)  # simulate manual labeling
end = time.time()
print("Manual triage time:", end - start)

# Assisted
start = time.time()
for e in emails:
    cat = clf.predict({"body": e})
    summary = summ.summarize(e)
    # simulate user approving instead of writing from scratch
    _ = user_review(cat, summary)
end = time.time()
print("Assisted triage time:", end - start)
