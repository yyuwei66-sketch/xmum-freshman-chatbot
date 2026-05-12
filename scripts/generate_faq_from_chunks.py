from pathlib import Path
from dotenv import load_dotenv
import os
import json
import time
import re
import requests

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3")

CHUNKS_DIR = Path("data/chunks")
OUTPUT_DIR = Path("data/processed/by_category")

# First full-category test: keep this small.
# Later you can change it to 10, 20, etc.
MAX_CHUNKS_PER_CATEGORY = 10
MAX_FAQ_PER_CHUNK = 3
SLEEP_SECONDS = 1.5

CATEGORY_CONFIG = {
    "academic_affairs": {
        "input_file": "academic_affairs_chunks.jsonl",
        "output_file": "academic_affairs.jsonl",
        "category_name": "Academic Affairs",
        "id_prefix": "AA"
    },
    "it_support": {
        "input_file": "it_support_chunks.jsonl",
        "output_file": "it_support.jsonl",
        "category_name": "University Platforms & IT Support",
        "id_prefix": "IT"
    },
    "registration_orientation": {
        "input_file": "registration_orientation_chunks.jsonl",
        "output_file": "registration_orientation.jsonl",
        "category_name": "Registration & Orientation",
        "id_prefix": "REG"
    },
    "campus_services": {
        "input_file": "campus_services_chunks.jsonl",
        "output_file": "campus_services.jsonl",
        "category_name": "Campus Services",
        "id_prefix": "CS"
    },
    "accommodation_living": {
        "input_file": "accommodation_living_chunks.jsonl",
        "output_file": "accommodation_living.jsonl",
        "category_name": "Accommodation & Living",
        "id_prefix": "AL"
    },
    "transportation": {
        "input_file": "transportation_chunks.jsonl",
        "output_file": "transportation.jsonl",
        "category_name": "Transportation",
        "id_prefix": "TR"
    },
    "finance_fees": {
        "input_file": "finance_fees_chunks.jsonl",
        "output_file": "finance_fees.jsonl",
        "category_name": "Finance & Fees",
        "id_prefix": "FIN"
    }
}

VALID_CATEGORIES = {
    "Academic Affairs",
    "University Platforms & IT Support",
    "Registration & Orientation",
    "Campus Services",
    "Accommodation & Living",
    "Transportation",
    "Finance & Fees"
}

VALID_INTENTS = {
    "ask_procedure",
    "ask_location",
    "ask_deadline",
    "ask_contact",
    "ask_definition"
}

REQUIRED_FIELDS = [
    "id",
    "category",
    "sub_category",
    "question",
    "answer",
    "keywords",
    "intent",
    "contributor",
    "verified"
]


def load_jsonl(path):
    items = []

    if not path.exists():
        return items

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    return items


def write_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def build_prompt(chunk, category_name, id_prefix):
    return f"""
You are helping build a FAQ dataset for a freshman enquiry chatbot at Xiamen University Malaysia.

Read the following handbook text chunk and generate FAQ entries in strict JSON array format.

Important:
The dataset does not use a separate student_type field.
If the answer differs for undergraduate, foundation, postgraduate, MBA, or international students, combine the differences inside the "answer" field using clear paragraphs such as:
"For undergraduate students: ..."
"For international students: ..."

Rules:
1. Only use information explicitly stated in the text chunk.
2. Do not invent deadlines, locations, fees, URLs, office names, email addresses, or procedures.
3. If the text does not contain useful FAQ information, return an empty JSON array [].
4. The "category" must be exactly:
   - {category_name}
5. The "intent" must be one of:
   - ask_procedure
   - ask_location
   - ask_deadline
   - ask_contact
   - ask_definition
6. The question must be a complete natural English question.
7. The answer must be clear, useful, and based only on the text.
8. If different student groups have different rules, explain them clearly inside the answer.
9. "keywords" should contain 3 to 6 lowercase English keywords.
10. "verified" must always be false.
11. Generate at most {MAX_FAQ_PER_CHUNK} FAQ entries from this chunk.
12. Return only a valid JSON array. Do not use markdown. Do not explain.

Required JSON fields:
id, category, sub_category, question, answer, keywords, intent, contributor, verified

Temporary ID rule:
Use temporary ids like "{id_prefix}_TEMP_001". The script will replace them later.

Contributor:
data_lead

Text chunk:
{chunk["content"]}
""".strip()


def call_llm(prompt):
    if not API_KEY:
        raise ValueError("LLM_API_KEY is missing. Please set it in .env")

    if not BASE_URL:
        raise ValueError("LLM_BASE_URL is missing. Please set it in .env")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"API error {response.status_code}: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def extract_json_array(text):
    text = text.strip()

    # Remove markdown code fences if the model accidentally returns them.
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON array found in model output.")

    json_text = text[start:end + 1]
    return json.loads(json_text)


def is_valid_item(item, expected_category):
    for field in REQUIRED_FIELDS:
        if field not in item:
            return False

    if item["category"] != expected_category:
        return False

    if item["category"] not in VALID_CATEGORIES:
        return False

    if item["intent"] not in VALID_INTENTS:
        return False

    if not isinstance(item["keywords"], list):
        return False

    if not (3 <= len(item["keywords"]) <= 6):
        return False

    if not isinstance(item["verified"], bool):
        return False

    if item["verified"] is not False:
        return False

    for keyword in item["keywords"]:
        if not isinstance(keyword, str):
            return False
        if keyword != keyword.lower():
            return False

    if not isinstance(item["question"], str):
        return False

    if not item["question"].strip().endswith("?"):
        return False

    if not isinstance(item["answer"], str):
        return False

    if item["answer"].strip() == "":
        return False

    return True


def remove_duplicate_questions(items):
    seen = set()
    unique_items = []

    for item in items:
        normalized_question = item["question"].strip().lower()

        if normalized_question in seen:
            continue

        seen.add(normalized_question)
        unique_items.append(item)

    return unique_items


def assign_ids(items, id_prefix):
    for index, item in enumerate(items, start=1):
        item["id"] = f"{id_prefix}_{index:03d}"

    return items


def generate_for_category(category_key, config):
    input_file = CHUNKS_DIR / config["input_file"]
    output_file = OUTPUT_DIR / config["output_file"]

    category_name = config["category_name"]
    id_prefix = config["id_prefix"]

    chunks = load_jsonl(input_file)

    if not chunks:
        print(f"\n[SKIP] No chunks found for {category_name}")
        return

    selected_chunks = chunks[:MAX_CHUNKS_PER_CATEGORY]

    print("\n" + "=" * 70)
    print(f"Processing category: {category_name}")
    print(f"Input file: {input_file}")
    print(f"Selected chunks: {len(selected_chunks)}")
    print("=" * 70)

    all_faqs = []

    for index, chunk in enumerate(selected_chunks, start=1):
        print(f"[{index}/{len(selected_chunks)}] {chunk.get('title', 'Untitled')}")

        prompt = build_prompt(chunk, category_name, id_prefix)

        try:
            raw_output = call_llm(prompt)
            faq_items = extract_json_array(raw_output)

            valid_items = [
                item for item in faq_items
                if is_valid_item(item, category_name)
            ]

            all_faqs.extend(valid_items)

            print(f"  Valid FAQ entries: {len(valid_items)}")

        except Exception as e:
            print(f"  Failed on chunk {chunk.get('chunk_id', 'unknown')}: {e}")

        time.sleep(SLEEP_SECONDS)

    all_faqs = remove_duplicate_questions(all_faqs)
    all_faqs = assign_ids(all_faqs, id_prefix)

    write_jsonl(output_file, all_faqs)

    print(f"Saved {len(all_faqs)} FAQ entries to {output_file}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_categories = len(CATEGORY_CONFIG)

    print(f"Starting FAQ generation for {total_categories} categories.")
    print(f"MAX_CHUNKS_PER_CATEGORY = {MAX_CHUNKS_PER_CATEGORY}")
    print(f"MAX_FAQ_PER_CHUNK = {MAX_FAQ_PER_CHUNK}")

    for category_key, config in CATEGORY_CONFIG.items():
        generate_for_category(category_key, config)

    print("\nFAQ generation completed.")


if __name__ == "__main__":
    main()