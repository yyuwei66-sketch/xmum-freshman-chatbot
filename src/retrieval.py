from pathlib import Path
import json
import re

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.preprocessing import normalize_text, preprocess_text, remove_stopwords, tokenize
from src.rule_classify import process_user_query


ROOT_DIR=Path(__file__).parent.parent
DATA_DIR=ROOT_DIR/"data"/"final"
EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
FALLBACK_SCORE_THRESHOLD=0.2
MIN_RETRIEVAL_EVIDENCE=0.25
RRF_K=60
RRF_TIE_EPSILON=0.01
_embedding_cache={}


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


def encode_texts(texts):
    """Encode texts with unit-normalized MiniLM embeddings."""
    if not texts:
        return np.empty((0,embedding_dimension),dtype=float)

    missing_texts=[]
    for text in texts:
        if text not in _embedding_cache:
            missing_texts.append(text)

    if missing_texts:
        embeddings=embedding_model.encode(
            missing_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        for text,embedding in zip(missing_texts,embeddings):
            _embedding_cache[text]=embedding

    return np.vstack([_embedding_cache[text] for text in texts])


def candidate_token_text(item):
    """Build the candidate text used for token-level semantic matching."""
    return " ".join([
        item.get("question",""),
        " ".join(item.get("keywords",[]))
    ])


def unique_tokens(text):
    """Tokenize text for semantic token matching, preserving first occurrence."""
    seen=set()
    result=[]
    for token in remove_stopwords(tokenize(text)):
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result


def rank_descending(scores):
    """Return one-based ranks where a larger score gets a smaller rank."""
    order=np.argsort(-scores,kind="mergesort")
    ranks=np.empty(len(scores),dtype=int)
    ranks[order]=np.arange(1,len(scores)+1)
    return ranks


def normalized_rrf_score(*rank_arrays):
    """Calculate normalized reciprocal rank fusion scores."""
    if not rank_arrays:
        return np.zeros(len(qa_pairs),dtype=float)

    raw_scores=np.zeros(len(rank_arrays[0]),dtype=float)
    for ranks in rank_arrays:
        raw_scores+=1.0/(RRF_K+ranks)

    max_score=len(rank_arrays)/(RRF_K+1)
    return np.clip(raw_scores/max_score,0.0,1.0)


def max_token_similarity(query_embeddings, candidate_embeddings):
    """Average each query token's best semantic match in one candidate."""
    if query_embeddings.size == 0 or candidate_embeddings.size == 0:
        return 0.0

    similarities=query_embeddings @ candidate_embeddings.T
    return float(np.mean(np.max(similarities,axis=1)))


def token_embedding_similarities(query_tokens):
    """Score query tokens against each FAQ candidate's question + keywords."""
    query_embeddings=encode_texts(query_tokens)
    return np.array([
        max_token_similarity(query_embeddings,candidate_embeddings)
        for candidate_embeddings in candidate_token_embeddings
    ],dtype=float)


def get_important_keyword(user_question):
    """
    Return the highest-IDF non-stopword query token.

    The IDF values come from FAQ question tokens and are used only to choose the
    query token for the keyword tie-breaker.
    """
    tokens=remove_stopwords(tokenize(user_question))
    scored_tokens=[]

    for token in tokens:
        vocab_index=keyword_vectorizer.vocabulary_.get(token)
        if vocab_index is not None:
            scored_tokens.append((float(keyword_idf[vocab_index]),token))

    if not scored_tokens:
        return None

    scored_tokens.sort(reverse=True)
    return scored_tokens[0][1]


def keyword_token_similarities(important_keyword):
    """Score the important keyword against each candidate's closest token."""
    if not important_keyword:
        return np.zeros(len(qa_pairs),dtype=float)

    keyword_embedding=encode_texts([important_keyword])
    return np.array([
        max_token_similarity(keyword_embedding,candidate_embeddings)
        for candidate_embeddings in candidate_token_embeddings
    ],dtype=float)


def build_retrieval_scores(user_question):
    """Build final RRF scores, keyword tie-break scores, and evidence scores."""
    question_embedding=encode_texts([user_question])
    sentence_embedding_similarities=question_embeddings @ question_embedding[0]

    tfidf_vector=sentence_vectorizer.transform([user_question])
    tfidf_sentence_similarities=cosine_similarity(tfidf_vector,sentence_question_vectors)[0]

    query_tokens=remove_stopwords(tokenize(user_question))
    embedding_token_similarities=token_embedding_similarities(query_tokens)

    important_keyword=get_important_keyword(user_question)
    keyword_similarities=keyword_token_similarities(important_keyword)

    final_scores=normalized_rrf_score(
        rank_descending(sentence_embedding_similarities),
        rank_descending(tfidf_sentence_similarities),
        rank_descending(embedding_token_similarities)
    )
    evidence_scores=np.maximum.reduce([
        sentence_embedding_similarities,
        tfidf_sentence_similarities,
        embedding_token_similarities
    ])

    has_lexical_anchor=important_keyword is not None or float(np.max(tfidf_sentence_similarities)) > 0.0

    return final_scores,keyword_similarities,evidence_scores,has_lexical_anchor


def score_sort_key(result):
    """
    Sort by RRF score, using keyword similarity only when scores are close.

    The score bucket implements the tie window without changing the public
    confidence score returned to callers.
    """
    score,keyword_similarity,_,index=result
    score_bucket=round(score/RRF_TIE_EPSILON)
    return (score_bucket,keyword_similarity,score,-index)


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

    question_embedding=encode_texts([user_question])
    similarities=question_embeddings @ question_embedding[0]
    best_index=similarities.argmax()

    return {
        "intent": qa_pairs[best_index].get("intent","faq_query"),
        "score": float(similarities[best_index]),
        "is_rule_based": False,
        "response": None
    }


def select_response(user_question, intent_info, entities):
    """
    Response selection layer.

    Select the best matching FAQ answer using RRF over sentence embedding,
    sentence TF-IDF, and semantic token rankings. Keyword similarity is used
    only as a tie-breaker when RRF scores are close.
    """
    del intent_info, entities

    if not user_question.strip():
        return {
            "answer": "Sorry, I do not have an answer for that.",
            "score": 0.0,
            "category": "Unknown",
            "matched_question": None,
            "related_questions": []
        }

    scores,keyword_similarities,evidence_scores,has_lexical_anchor=build_retrieval_scores(user_question)
    scored_results=[
        (
            float(scores[index]),
            float(keyword_similarities[index]),
            float(evidence_scores[index]),
            index
        )
        for index in range(len(qa_pairs))
    ]
    scored_results.sort(key=score_sort_key,reverse=True)

    best_score,_,best_evidence,best_index=scored_results[0]
    related_questions=[
        qa_pairs[index]["question"]
        for _,_,_,index in scored_results[1:4]
    ]

    should_fallback=(
        not has_lexical_anchor
        or best_score < FALLBACK_SCORE_THRESHOLD
        or best_evidence < MIN_RETRIEVAL_EVIDENCE
    )

    if should_fallback:
        fallback_score=0.0 if not has_lexical_anchor else min(best_score,best_evidence)
        return {
            "answer": "Sorry, I do not have an answer for that.",
            "score": fallback_score,
            "category": "Unknown",
            "matched_question": None,
            "related_questions": related_questions
        }

    return {
        "answer": qa_pairs[best_index]["answer"],
        "score": best_score,
        "category": qa_pairs[best_index].get("category", "Unknown"),
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
                "category": "General Conversation",
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

questions=[item["question"] for item in qa_pairs]
tokenized_questions=[preprocess_text(question) for question in questions]
candidate_tokens=[unique_tokens(candidate_token_text(item)) for item in qa_pairs]
tokenized_candidate_texts=[" ".join(tokens) for tokens in candidate_tokens]
entity_vocabulary=build_entity_vocabulary(qa_pairs)

try:
    # Avoid a network metadata check when the model is already cached.
    embedding_model=SentenceTransformer(EMBEDDING_MODEL_NAME,local_files_only=True)
except OSError:
    # A fresh installation can still download the model in the usual way.
    embedding_model=SentenceTransformer(EMBEDDING_MODEL_NAME)
if hasattr(embedding_model,"get_embedding_dimension"):
    embedding_dimension=embedding_model.get_embedding_dimension()
else:
    embedding_dimension=embedding_model.get_sentence_embedding_dimension()
question_embeddings=encode_texts(questions)
candidate_token_embeddings=[
    encode_texts(tokens)
    for tokens in candidate_tokens
]

sentence_vectorizer=TfidfVectorizer(ngram_range=(1,2))
sentence_question_vectors=sentence_vectorizer.fit_transform(questions)

keyword_vectorizer=TfidfVectorizer()
keyword_vectorizer.fit(tokenized_candidate_texts)
keyword_idf=keyword_vectorizer.idf_


def get_response(user_question):
    return chatbot_pipeline(user_question)["response"]


if __name__ == "__main__":
    while True:
        user_input=input("You: ")

        if user_input.lower() == "exit":
            break

        print("Bot:", get_response(user_input))
