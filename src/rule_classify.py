import re
from typing import Dict, Optional, Any

from src.preprocessing import normalize_text, preprocess_text


RULE_BASED_RESPONSES: Dict[str, str] = {
    "greeting": "Hello! I am the XMUM Freshman FAQ Chatbot. How can I help you?",
    "thanks": "You are welcome! Feel free to ask another question.",
    "goodbye": "Goodbye! Have a nice day.",
    "help": (
        "You can ask me questions about academic affairs, university platforms, "
        "IT support, registration, orientation, campus services, accommodation, "
        "transportation, and payment."
    ),
    "identity": (
        "I am a hybrid FAQ chatbot designed to help XMUM freshmen find "
        "campus-related information."
    )
}


INTENT_PATTERNS: Dict[str, list] = {
    "greeting": [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ],
    "thanks": [
        "thanks",
        "thank you",
        "thx",
        "thank"
    ],
    "goodbye": [
        "bye",
        "goodbye",
        "see you",
        "see ya"
    ],
    "help": [
        "help",
        "what can you do",
        "how can you help",
        "what can i ask"
    ],
    "identity": [
        "who are you",
        "what are you",
        "are you a chatbot",
        "your name"
    ]
}


def detect_intent(user_query: str) -> Optional[str]:
    """
    Detect simple rule-based intent.

    This function uses word boundary matching to avoid false matches.
    Example:
    - "hi" should match greeting
    - "this is my question" should not match greeting
    """
    normalized_query = normalize_text(user_query)

    if not normalized_query:
        return None

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            normalized_pattern = normalize_text(pattern)

            regex_pattern = r"\b" + re.escape(normalized_pattern) + r"\b"

            if re.search(regex_pattern, normalized_query):
                return intent

    return None


def get_rule_based_response(intent: str) -> Optional[str]:
    """
    Return predefined response according to detected intent.
    """
    return RULE_BASED_RESPONSES.get(intent)


def process_user_query(user_query: str) -> Dict[str, Any]:
    """
    Combined NLP layer.

    This function should be called before ML classification.

    If the input is a simple conversational intent:
        return rule-based response directly

    If the input is a FAQ query:
        route it to ML classification
    """
    cleaned_query = preprocess_text(user_query)
    detected_intent = detect_intent(user_query)

    if detected_intent is not None:
        return {
            "original_query": user_query,
            "cleaned_query": cleaned_query,
            "is_rule_based": True,
            "intent": detected_intent,
            "response": get_rule_based_response(detected_intent),
            "route": "rule_based"
        }

    return {
        "original_query": user_query,
        "cleaned_query": cleaned_query,
        "is_rule_based": False,
        "intent": "faq_query",
        "response": None,
        "route": "ml_classification"
    }