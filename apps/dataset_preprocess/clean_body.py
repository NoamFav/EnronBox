import re

def clean_body(text):
    text = re.sub(r'From:.*\n', '', text)
    text = re.sub(r'Sent:.*\n', '', text)
    text = re.sub(r'To:.*\n', '', text)
    text = re.sub(r'Subject:.*\n', '', text)

    text = re.sub(r'On .* wrote:\n.*', '', text, flags=re.DOTALL)
    
    text = re.sub(r'--\s.*', '', text, flags=re.DOTALL)
    return text.strip()
