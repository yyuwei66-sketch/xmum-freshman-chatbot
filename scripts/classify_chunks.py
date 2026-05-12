from pathlib import Path
import json

INPUT_FILE = Path("data/chunks/all_chunks.jsonl")
OUTPUT_DIR = Path("data/chunks")

CATEGORY_KEYWORDS = {
    "academic_affairs": [
        "course", "registration", "add/drop", "add drop", "attendance",
        "cgpa", "gpa", "exam", "quiz", "test", "academic calendar",
        "timetable", "credit", "graduation", "dean", "appeal", "grade",
        "assessment", "semester", "programme", "program"
    ],
    "it_support": [
        "moodle", "student portal", "portal", "outlook", "email",
        "wifi", "wi-fi", "network", "password", "login", "account",
        "eduroam", "e-learning", "online learning"
    ],
    "registration_orientation": [
        "orientation", "new student", "student card",
        "document submission", "briefing", "freshman", "enrolment",
        "enrollment", "arrival", "checklist", "registration day"
    ],
    "campus_services": [
        "library", "clinic", "security", "printing", "lost and found",
        "student affairs", "counselling", "counseling", "medical",
        "health", "office", "facility", "facilities"
    ],
    "accommodation_living": [
        "hostel", "accommodation", "room", "maintenance", "laundry",
        "water", "electricity", "visitor", "key", "residence",
        "dormitory", "check-in", "check out", "check-out"
    ],
    "transportation": [
        "bus", "shuttle", "transport", "transportation", "airport",
        "taxi", "grab", "pick-up", "pickup", "vehicle", "parking",
        "entrance", "gate"
    ],
    "finance_fees": [
        "fee", "fees", "tuition", "payment", "refund", "scholarship",
        "finance", "invoice", "receipt", "deadline", "penalty",
        "deposit", "bank", "billing", "financial"
    ]
}


def load_jsonl(path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def write_jsonl(path, items):
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def classify_chunk(chunk):
    text = (chunk["title"] + "\n" + chunk["content"]).lower()

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "uncategorized"

    return best_category


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chunks = load_jsonl(INPUT_FILE)

    grouped = {category: [] for category in CATEGORY_KEYWORDS.keys()}
    grouped["uncategorized"] = []

    for chunk in chunks:
        category = classify_chunk(chunk)
        grouped[category].append(chunk)

    for category, items in grouped.items():
        output_file = OUTPUT_DIR / f"{category}_chunks.jsonl"
        write_jsonl(output_file, items)
        print(f"{category}: {len(items)} chunks")


if __name__ == "__main__":
    main()