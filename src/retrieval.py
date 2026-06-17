from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from src.rule_classify import process_user_query
from src.preprocessing import normalize_text, preprocess_text, tokenize, remove_stopwords
import json
import numpy as np
import re

ROOT_DIR=Path(__file__).parent.parent
DATA_DIR=ROOT_DIR/"data"/"final"
FALLBACK_SCORE_THRESHOLD=0.2


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

    user_vector=sentence_vectorizer.transform([user_question])
    similarities=cosine_similarity(user_vector, sentence_question_vectors)[0]
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


def build_keyword_search_text(item):
    """Build the text used to check whether an important keyword is present."""
    return normalize_text(
        " ".join([
            item.get("question",""),
            " ".join(item.get("keywords",[]))
        ])
    )


def get_important_keyword(user_question):
    """
    Return the highest-IDF non-stopword query token.

    This is a lightweight proxy for the most specific word in the user's
    question. It uses the token-level FAQ vectorizer vocabulary.
    """
    tokens=remove_stopwords(tokenize(user_question))
    scored_tokens=[]

    for token in tokens:
        vocab_index=token_vectorizer.vocabulary_.get(token)
        if vocab_index is not None:
            scored_tokens.append((float(token_idf[vocab_index]),token))

    if not scored_tokens:
        return None

    scored_tokens.sort(reverse=True)
    return scored_tokens[0][1]


def keyword_missing_penalty(important_keyword, item):
    """Return -1.0 when the candidate FAQ misses the important query keyword."""
    if not important_keyword:
        return 0.0

    if contains_normalized_phrase(item_keyword_texts[item["__index__"]],important_keyword):
        return 0.0

    return -1.0


def build_scoring_features(user_question, intent_info, entities):
    """Build one feature row per FAQ candidate for the trainable scorer."""
    sentence_vector=sentence_vectorizer.transform([user_question])
    sentence_similarities=cosine_similarity(sentence_vector,sentence_question_vectors)[0]

    token_text=preprocess_text(user_question)
    token_vector=token_vectorizer.transform([token_text])
    token_similarities=cosine_similarity(token_vector,token_question_vectors)[0]

    important_keyword=get_important_keyword(user_question)
    features=[]

    for index,item in enumerate(qa_pairs):
        intent_match=1.0 if item.get("intent") == intent_info["intent"] else 0.0
        entity_overlap=entity_overlap_score(item,entities)
        keyword_penalty=keyword_missing_penalty(important_keyword,item)

        features.append([
            float(sentence_similarities[index]),
            float(token_similarities[index]),
            keyword_penalty,
            intent_match,
            entity_overlap
        ])

    return np.array(features,dtype=float)


def clip_score(score):
    """Calibrate and keep public confidence scores in a predictable 0..1 range."""
    calibrated=(score-retrieval_null_score)/(1.0-retrieval_null_score)
    return float(np.clip(calibrated,0.0,1.0))


def train_retrieval_scorer():
    """
    Fit the linear retrieval scorer with weak supervision.

    Each FAQ's original question is treated as a positive match for itself and
    as a negative match for all other FAQ records. This gives fitted feature
    weights without requiring a manually labelled query-to-FAQ dataset.
    """
    feature_rows=[]
    labels=[]
    sample_weights=[]
    negative_weight=1.0/(len(qa_pairs)-1)

    for query_index,question in enumerate(questions):
        entities=extract_entities(question)
        intent_info={
            "intent": qa_pairs[query_index].get("intent","faq_query"),
            "score": 1.0,
            "is_rule_based": False,
            "response": None
        }
        query_features=build_scoring_features(question,intent_info,entities)

        for candidate_index,row in enumerate(query_features):
            is_positive=candidate_index == query_index
            feature_rows.append(row)
            labels.append(1.0 if is_positive else 0.0)
            sample_weights.append(1.0 if is_positive else negative_weight)

    scorer=Ridge(alpha=1.0)
    scorer.fit(np.array(feature_rows),np.array(labels),sample_weight=np.array(sample_weights))
    return scorer


def select_response(user_question, intent_info, entities):
    """
    Response selection layer.

    Select the best matching FAQ answer with a weakly supervised linear
    combination of sentence similarity, token similarity, keyword penalty,
    intent match, and entity overlap.
    """
    features=build_scoring_features(user_question,intent_info,entities)
    scores=retrieval_scorer.predict(features)

    scored_results=[]
    for index,item in enumerate(qa_pairs):
        score=clip_score(scores[index])
        scored_results.append((score,index))

    scored_results.sort(reverse=True)
    best_score,best_index=scored_results[0]
    related_questions=[
        qa_pairs[index]["question"]
        for _,index in scored_results[1:4]
    ]

    if best_score < FALLBACK_SCORE_THRESHOLD:
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
for index,item in enumerate(qa_pairs):
    item["__index__"]=index

questions = [item["question"] for item in qa_pairs]
tokenized_questions = [preprocess_text(question) for question in questions]
entity_vocabulary=build_entity_vocabulary(qa_pairs)
item_keyword_texts=[build_keyword_search_text(item) for item in qa_pairs]

sentence_vectorizer = TfidfVectorizer(ngram_range=(1,2))
sentence_question_vectors = sentence_vectorizer.fit_transform(questions)

token_vectorizer = TfidfVectorizer()
token_question_vectors = token_vectorizer.fit_transform(tokenized_questions)
token_idf = token_vectorizer.idf_

retrieval_scorer = train_retrieval_scorer()
retrieval_null_score = float(retrieval_scorer.predict(np.zeros((1,5)))[0])


def get_response(user_question):
    return chatbot_pipeline(user_question)["response"]


if __name__ == "__main__":
    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        print("Bot:", get_response(user_input))
