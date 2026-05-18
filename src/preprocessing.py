import re
from typing import List


STOPWORDS = {
    "a", "an", "the",
    "is", "are", "am", "was", "were",
    "do", "does", "did",
    "can", "could", "would", "should",
    "i", "me", "my", "you", "your", "we", "our",
    "to", "for", "of", "in", "on", "at", "by", "with",
    "and", "or", "but", "so", "if", "then",
    "please"
}


def normalize_text(text: str) -> str:
    """
    Convert text to lowercase and remove punctuation.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


def tokenize(text: str) -> List[str]:
    """
    Split normalized text into tokens.
    """
    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    return normalized_text.split()


def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Remove common stopwords.
    """
    return [token for token in tokens if token not in STOPWORDS]


def simple_stem(word: str) -> str:
    """
    Simple stemming for prototype use.
    """
    suffixes = ["ing", "ed", "es", "s"]

    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]

    return word


def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline:
    normalization -> tokenization -> stopword removal -> simple stemming
    """
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = [simple_stem(token) for token in tokens]

    return " ".join(tokens)