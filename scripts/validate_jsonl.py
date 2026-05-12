from pathlib import Path
import json

INPUT_DIR = Path("data/processed/by_category")

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


def validate_item(item, file_name, line_number):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in item:
            errors.append(f"Missing field: {field}")

    if "category" in item and item["category"] not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {item['category']}")

    if "intent" in item and item["intent"] not in VALID_INTENTS:
        errors.append(f"Invalid intent: {item['intent']}")

    if "keywords" in item:
        if not isinstance(item["keywords"], list):
            errors.append("keywords must be a list")
        elif not (3 <= len(item["keywords"]) <= 6):
            errors.append("keywords must contain 3 to 6 words")
        else:
            for keyword in item["keywords"]:
                if not isinstance(keyword, str):
                    errors.append("each keyword must be a string")
                elif keyword != keyword.lower():
                    errors.append(f"keyword should be lowercase: {keyword}")

    if "verified" in item and not isinstance(item["verified"], bool):
        errors.append("verified must be true or false")

    for field in ["id", "category", "sub_category", "question", "answer", "intent", "contributor"]:
        if field in item and not isinstance(item[field], str):
            errors.append(f"{field} must be a string")
        elif field in item and item[field].strip() == "":
            errors.append(f"{field} cannot be empty")

    if "question" in item and not item["question"].strip().endswith("?"):
        errors.append("question should end with a question mark")

    if errors:
        print(f"\nError in {file_name}, line {line_number}:")
        for error in errors:
            print(f"  - {error}")
        print(f"  Data: {item}")

    return len(errors) == 0


def main():
    jsonl_files = sorted(INPUT_DIR.glob("*.jsonl"))

    if not jsonl_files:
        print("No JSONL files found in data/processed/by_category/")
        return

    total = 0
    valid = 0
    seen_ids = set()
    duplicate_ids = []

    for file_path in jsonl_files:
        with file_path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()

                if not line:
                    continue

                total += 1

                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"\nJSON error in {file_path.name}, line {line_number}: {e}")
                    continue

                if "id" in item:
                    if item["id"] in seen_ids:
                        duplicate_ids.append(item["id"])
                    else:
                        seen_ids.add(item["id"])

                if validate_item(item, file_path.name, line_number):
                    valid += 1

    print("\nValidation summary:")
    print(f"Total entries: {total}")
    print(f"Valid entries: {valid}")
    print(f"Invalid entries: {total - valid}")

    if duplicate_ids:
        print("\nDuplicate IDs found:")
        for item_id in duplicate_ids:
            print(f"  - {item_id}")

    if total == valid and not duplicate_ids:
        print("All JSONL files are valid.")
    else:
        print("Some problems need to be fixed.")


if __name__ == "__main__":
    main()