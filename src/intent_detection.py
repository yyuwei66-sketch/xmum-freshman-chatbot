import re
from typing import Any, Dict, List, Optional

from src.preprocessing import normalize_domain_terms, preprocess_text, tokenize


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


CONVERSATIONAL_INTENT_RULES: List[Dict[str, Any]] = [
    {
        "intent": "goodbye",
        "patterns": ["bye", "goodbye", "see you", "see ya"],
        "priority": 100,
    },
    {
        "intent": "thanks",
        "patterns": ["thanks", "thank you", "thx", "thank"],
        "priority": 90,
    },
    {
        "intent": "help",
        "patterns": [
            "help",
            "what can you do",
            "how can you help",
            "what can i ask",
        ],
        "priority": 80,
    },
    {
        "intent": "identity",
        "patterns": [
            "who are you",
            "what are you",
            "are you a chatbot",
            "your name",
        ],
        "priority": 70,
    },
    {
        "intent": "greeting",
        "patterns": [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ],
        "priority": 60,
    },
]

FAQ_TEMPLATE_RULES: List[Dict[str, Any]] = [
    {
        "intent": "ask_location",
        "patterns": [
            r"\bwhere (is|are|can i find|can i get)\b",
            r"\bhow (do|can) i get to\b",
            r"\blocation of\b",
        ],
        "keywords": ["where", "location", "located", "find", "address"],
    },
    {
        "intent": "ask_contact",
        "patterns": [
            r"\bwho (do|should|can) i contact\b",
            r"\bhow (do|can) i contact\b",
            r"\bcontact (number|email|person|office)\b",
        ],
        "keywords": ["contact", "email", "phone", "office", "hotline"],
    },
    {
        "intent": "ask_procedure",
        "patterns": [
            r"\bhow (do|can|should) i\b",
            r"\bwhat (do|should) i do\b",
            r"\bsteps? to\b",
            r"\bprocedure for\b",
        ],
        "keywords": [
            "apply",
            "register",
            "reset",
            "submit",
            "book",
            "login",
            "pay",
        ],
    },
    {
        "intent": "ask_deadline",
        "patterns": [
            r"\bwhen (is|are|do|does|should|can)\b",
            r"\bwhat (is|are) the deadline\b",
            r"\bby when\b",
            r"\bdue date\b",
        ],
        "keywords": ["when", "deadline", "due", "date", "calendar"],
    },
    {
        "intent": "ask_definition",
        "patterns": [
            r"\bwhat (is|are)\b",
            r"\bwhat does .+ mean\b",
            r"\bexplain\b",
        ],
        "keywords": ["what", "define", "meaning", "explain"],
    },
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Academic Affairs": [
        "academic",
        "course",
        "exam",
        "grade",
        "cgpa",
        "timetable",
        "semester",
        "programme",
        "attendance",
    ],
    "University Platforms & IT Support": [
        "moodle",
        "studentportal",
        "email",
        "wifi",
        "password",
        "login",
        "account",
        "elearning",
    ],
    "Registration & Orientation": [
        "registration",
        "orientation",
        "freshman",
        "student card",
        "enrolment",
        "enrollment",
    ],
    "Campus Services": [
        "library",
        "clinic",
        "security",
        "printing",
        "counselling",
        "facility",
    ],
    "Accommodation & Living": [
        "hostel",
        "accommodation",
        "room",
        "laundry",
        "maintenance",
        "checkin",
        "checkout",
    ],
    "Transportation": [
        "bus",
        "shuttle",
        "transport",
        "airport",
        "parking",
        "pickup",
    ],
    "Finance & Fees": [
        "fee",
        "fees",
        "tuition",
        "payment",
        "refund",
        "scholarship",
        "invoice",
    ],
}


def _match_phrase_patterns(
    normalized_query: str,
    rules: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    matches = []

    for rule in rules:
        for pattern in rule["patterns"]:
            normalized_pattern = normalize_domain_terms(pattern)
            regex_pattern = r"\b" + re.escape(normalized_pattern) + r"\b"

            if re.search(regex_pattern, normalized_query):
                matches.append({
                    "intent": rule["intent"],
                    "matched_pattern": pattern,
                    "confidence": 1.0,
                    "priority": rule["priority"],
                })

    if not matches:
        return None

    return max(matches, key=lambda match: match["priority"])


def detect_intent(user_query: str) -> Optional[str]:
    """
    Detect simple conversational intent.

    This function uses word boundary matching to avoid false matches.
    Example:
    - "hi" should match greeting
    - "this is my question" should not match greeting
    """
    match = detect_conversation_intent(user_query)

    if match is None:
        return None

    return match["intent"]


def detect_conversation_intent(user_query: str) -> Optional[Dict[str, Any]]:
    """
    Detect rule-based conversational intent for fast direct responses.
    """
    normalized_query = normalize_domain_terms(user_query)

    if not normalized_query:
        return None

    match = _match_phrase_patterns(normalized_query, CONVERSATIONAL_INTENT_RULES)

    if match is None:
        return None

    return {
        "intent": match["intent"],
        "matched_pattern": match["matched_pattern"],
        "confidence": match["confidence"],
    }


def detect_faq_template_intent(user_query: str) -> Optional[Dict[str, Any]]:
    """
    Detect FAQ question type using hand-written templates and keywords.
    """
    normalized_query = normalize_domain_terms(user_query)

    if not normalized_query:
        return None

    tokens = set(tokenize(normalized_query))

    for rule in FAQ_TEMPLATE_RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, normalized_query):
                return {
                    "intent": rule["intent"],
                    "matched_pattern": pattern,
                    "confidence": 0.9,
                    "source": "template",
                }

    for rule in FAQ_TEMPLATE_RULES:
        matched_keywords = [
            keyword
            for keyword in rule["keywords"]
            if keyword in tokens or keyword in normalized_query
        ]

        if matched_keywords:
            return {
                "intent": rule["intent"],
                "matched_pattern": matched_keywords[0],
                "confidence": 0.65,
                "source": "keyword",
            }

    return {
        "intent": "ask_general",
        "matched_pattern": None,
        "confidence": 0.4,
        "source": "fallback",
    }


def detect_category_hint(user_query: str) -> Optional[str]:
    """
    Return a lightweight category hint for downstream classification/retrieval.
    """
    normalized_query = normalize_domain_terms(user_query)

    if not normalized_query:
        return None

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            normalized_keyword = normalize_domain_terms(keyword)
            pattern = r"\b" + re.escape(normalized_keyword) + r"\b"

            if re.search(pattern, normalized_query):
                score += 1

        if score > 0:
            scores[category] = score

    if not scores:
        return None

    return max(scores, key=scores.get)


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
    normalized_query = normalize_domain_terms(user_query)
    cleaned_query = preprocess_text(user_query)
    tokens = tokenize(user_query)
    conversation_intent = detect_conversation_intent(user_query)

    if conversation_intent is not None:
        detected_intent = conversation_intent["intent"]
        return {
            "original_query": user_query,
            "normalized_query": normalized_query,
            "cleaned_query": cleaned_query,
            "tokens": tokens,
            "is_rule_based": True,
            "intent": detected_intent,
            "faq_intent": None,
            "category_hint": None,
            "matched_pattern": conversation_intent["matched_pattern"],
            "intent_confidence": conversation_intent["confidence"],
            "response": get_rule_based_response(detected_intent),
            "route": "rule_based"
        }

    faq_intent = detect_faq_template_intent(user_query)
    category_hint = detect_category_hint(user_query)

    return {
        "original_query": user_query,
        "normalized_query": normalized_query,
        "cleaned_query": cleaned_query,
        "tokens": tokens,
        "is_rule_based": False,
        "intent": "faq_query",
        "faq_intent": faq_intent["intent"] if faq_intent else None,
        "category_hint": category_hint,
        "matched_pattern": faq_intent["matched_pattern"] if faq_intent else None,
        "intent_confidence": faq_intent["confidence"] if faq_intent else 0.0,
        "response": None,
        "route": "ml_classification"
    }
