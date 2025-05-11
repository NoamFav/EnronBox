from sklearn.feature_extraction.text import TfidfVectorizer

def vectorize_texts(texts):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    return X
