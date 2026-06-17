from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from src.rule_classify import process_user_query
from src.preprocessing import normalize_text, tokenize, remove_stopwords
import json
import re

ROOT_DIR=Path(__file__).parent.parent
DATA_DIR=ROOT_DIR/"data"/"final"


def load_jsonl(file_path):
    """Load FAQ records from a JSONL file."""
    with open(file_path,"r",encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_entity_vocabulary(records):
    """Build a small entity vocabulary from FAQ metadata."""
    vocabulary={
        "keywords": set(),
        "categories": set(),
        "sub_categories": set()
    }

    for item in records:
        for keyword in item.get("keywords",[]):
            vocabulary["keywords"].add(normalize_text(keyword))

        category=normalize_text(item.get("category",""))
        sub_category=normalize_text(item.get("sub_category",""))

        if category:
            vocabulary["categories"].add(category)
        if sub_category:
            vocabulary["sub_categories"].add(sub_category)

    return vocabulary


def contains_normalized_phrase(text, phrase):
    """Return True when a normalized phrase appears on word boundaries."""
    if not phrase:
        return False

    pattern=r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern,text) is not None


def extract_entities(user_question):
    """
    Entity recognition layer.

    This prototype extracts structured clues from the query using regexes and
    FAQ metadata, such as dates, times, numbers, categories, and keywords.
    """
    normalized_query=normalize_text(user_question)
    tokens=remove_stopwords(tokenize(user_question))

    dates=re.findall(
        r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"january|february|march|april|may|june|july|august|september|"
        r"october|november|december)\b",
        normalized_query
    )
    times=re.findall(r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b", normalized_query)

    matched_keywords=[
        keyword for keyword in entity_vocabulary["keywords"]
        if contains_normalized_phrase(normalized_query,keyword)
    ]
    matched_categories=[
        category for category in entity_vocabulary["categories"]
        if contains_normalized_phrase(normalized_query,category)
    ]
    matched_sub_categories=[
        sub_category for sub_category in entity_vocabulary["sub_categories"]
        if contains_normalized_phrase(normalized_query,sub_category)
    ]

    return {
        "tokens": tokens,
        "dates": dates,
        "times": times,
        "keywords": matched_keywords,
        "categories": matched_categories,
        "sub_categories": matched_sub_categories
    }


def classify_intent(user_question):
    """
    Intent classification layer.

    Conversational intents are handled by rules. FAQ intents are estimated by
    comparing the user query with existing FAQ questions and taking the intent
    of the closest question.
    """
    query_info=process_user_query(user_question)

    if query_info["is_rule_based"]:
        return {
            "intent": query_info["intent"],
            "score": 1.0,
            "is_rule_based": True,
            "response": query_info["response"]
        }

    user_vector=vectorizer.transform([user_question])
    similarities=cosine_similarity(user_vector, question_vectors)[0]
    best_index=similarities.argmax()

    return {
        "intent": qa_pairs[best_index].get("intent","faq_query"),
        "score": float(similarities[best_index]),
        "is_rule_based": False,
        "response": None
    }


def entity_overlap_score(item, entities):
    """Score how many extracted entities match one FAQ record."""
    score=0.0

    item_keywords={
        normalize_text(keyword)
        for keyword in item.get("keywords",[])
    }
    score+=0.03*len(item_keywords.intersection(entities["keywords"]))

    category=normalize_text(item.get("category",""))
    sub_category=normalize_text(item.get("sub_category",""))

    if category in entities["categories"]:
        score+=0.05
    if sub_category in entities["sub_categories"]:
        score+=0.05

    item_text=normalize_text(
        " ".join([
            item.get("question",""),
            item.get("answer",""),
            " ".join(item.get("keywords",[]))
        ])
    )
    for token in entities["tokens"]:
        if token in item_text:
            score+=0.005

    return min(score,0.2)


def select_response(user_question, intent_info, entities):
    """
    Response selection layer.

    Select the best matching FAQ answer using TF-IDF similarity, then boost
    records that share the predicted intent and extracted entities.
    """
    user_vector=vectorizer.transform([user_question])
    similarities=cosine_similarity(user_vector, question_vectors)[0]

    scored_results=[]
    for index,item in enumerate(qa_pairs):
        score=float(similarities[index])

        if item.get("intent") == intent_info["intent"]:
            score+=0.05

        score+=entity_overlap_score(item, entities)
        scored_results.append((score,index))

    scored_results.sort(reverse=True)
    best_score,best_index=scored_results[0]
    related_questions=[
        qa_pairs[index]["question"]
        for _,index in scored_results[1:4]
    ]

    if best_score < 0.2:
        return {
            "answer": "Sorry, I do not have an answer for that.",
            "score": best_score,
            "matched_question": None,
            "related_questions": related_questions
        }

    return {
        "answer": qa_pairs[best_index]["answer"],
        "score": best_score,
        "matched_question": qa_pairs[best_index]["question"],
        "related_questions": related_questions
    }


def chatbot_pipeline(user_question):
    """
    Operational process:
    1. Intent classification
    2. Entity recognition
    3. Response selection
    """
    intent_info=classify_intent(user_question)

    if intent_info["is_rule_based"]:
        return {
            "intent": intent_info,
            "entities": {},
            "selection": {
                "answer": intent_info["response"],
                "score": intent_info["score"],
                "matched_question": None,
                "related_questions": []
            },
            "response": intent_info["response"]
        }

    entities=extract_entities(user_question)
    selection=select_response(user_question,intent_info,entities)

    return {
        "intent": intent_info,
        "entities": entities,
        "selection": selection,
        "response": selection["answer"]
    }


qa_pairs=load_jsonl(DATA_DIR/"faq_dataset_final_merged.jsonl")

questions = [item["question"] for item in qa_pairs]
entity_vocabulary=build_entity_vocabulary(qa_pairs)

vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(questions)


def get_response(user_question):
    return chatbot_pipeline(user_question)["response"]


if __name__ == "__main__":
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        print("Bot:", get_response(user_input))
