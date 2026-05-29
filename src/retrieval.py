from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import json

ROOT_DIR=Path(__file__).parent.parent
DATA_DIR=ROOT_DIR/"data"/"processed"
with open(DATA_DIR/"faq_dataset.json","r") as f:
    qa_pairs=json.load(f)   

questions = [item["question"] for item in qa_pairs]

vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(questions)


def get_response(user_question):
    user_vector = vectorizer.transform([user_question])

    similarities = cosine_similarity(user_vector, question_vectors)

    best_index = similarities.argmax()
    best_score = similarities[0][best_index]

    if best_score < 0.2:
        return "Sorry, I do not have an answer for that."

    return qa_pairs[best_index]["answer"]


while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    print("Bot:", get_response(user_input))
