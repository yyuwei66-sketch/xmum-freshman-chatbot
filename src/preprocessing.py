import re
from typing import Dict, List


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

DOMAIN_TERMS: Dict[str, str] = {
    "wi fi": "wifi",
    "wireless network": "wifi",
    "e learning": "elearning",
    "student portal": "studentportal",
    "outlook email": "email",
    "add drop": "adddrop",
    "check in": "checkin",
    "check out": "checkout",
    "xiamen university malaysia": "xmum",
}

STEM_EXCEPTIONS = {
    "bus",
    "campus",
    "class",
    "business",
    "fees",
    "moodle",
    "xmum",
}


def normalize_text(text: str) -> str:
    """
    Convert text to lowercase and normalize punctuation/spacing.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r"['`]", "", text)
    text = re.sub(r"[-/]", " ", text)
    text = re.sub(r"_", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_domain_terms(text: str) -> str:
    """
    Normalize common XMUM FAQ terms after basic text normalization.
    """
    normalized_text = normalize_text(text)

    for phrase, replacement in DOMAIN_TERMS.items():
        pattern = r"\b" + re.escape(phrase) + r"\b"
        normalized_text = re.sub(pattern, replacement, normalized_text)

    return re.sub(r"\s+", " ", normalized_text).strip()


def tokenize(text: str) -> List[str]:
    """
    Split normalized text into tokens.
    """
    normalized_text = normalize_domain_terms(text)

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
    Conservative rule-based stemming for prototype use.
    """
    if not isinstance(word, str):
        return ""

    if len(word) <= 4 or word in STEM_EXCEPTIONS:
        return word

    if word.endswith("ies") and len(word) > 5:
        return word[:-3] + "y"

    if word.endswith("ing") and len(word) > 6:
        stem = word[:-3]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        return stem

    if word.endswith("ed") and len(word) > 5:
        stem = word[:-2]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        return stem

    if word.endswith("es") and len(word) > 5:
        return word[:-2]

    if (
        word.endswith("s")
        and len(word) > 4
        and not word.endswith(("ss", "us"))
    ):
        return word[:-1]

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
