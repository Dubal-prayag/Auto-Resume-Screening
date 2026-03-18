import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def preprocess(text):

    text = text.lower()

    # Preserve alphanumeric, spaces, and essential tech punctuation (+, #, ., /)
    # This prevents destroying terms like C++, C#, .NET, Node.js, and CI/CD
    text = re.sub(r"[^a-z0-9\+\#\.\/\s]", " ", text)

    tokens = text.split()

    cleaned = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word not in stop_words and len(word) >= 2
    ]

    return " ".join(cleaned)