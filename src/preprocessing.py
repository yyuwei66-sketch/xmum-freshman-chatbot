from typing import List

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


TOKEN_ANALYZER = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
).build_analyzer()


def normalize_text(text: str) -> str:
    """
    Convert text to a lowercase, whitespace-separated token string.
    """
    if not isinstance(text, str):
        return ""

    return " ".join(TOKEN_ANALYZER(text))


def tokenize(text: str) -> List[str]:
    """
    Tokenize text using scikit-learn's default TF-IDF analyzer.
    """
    if not isinstance(text, str):
        return []

    return TOKEN_ANALYZER(text)


def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Remove English stop words using scikit-learn's built-in stop word list.
    """
    return [token for token in tokens if token not in ENGLISH_STOP_WORDS]


def preprocess_text(text: str) -> str:
    """
    Full preprocessing pipeline:
    scikit-learn tokenization -> built-in English stop word removal
    """
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)

    return " ".join(tokens)
