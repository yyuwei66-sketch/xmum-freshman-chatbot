from pathlib import Path
import json

INPUT_DIR = Path("data/processed/by_category")
OUTPUT_FILE = Path("data/processed/faq_dataset.jsonl")

CATEGORY_FILES = [
    "academic_affairs.jsonl",
    "it_support.jsonl",
    "registration_orientation.jsonl",
    "campus_services.jsonl",
    "accommodation_living.jsonl",
    "transportation.jsonl",
    "finance_fees.jsonl"
]


def main():
    merged_items = []

    for file_name in CATEGORY_FILES:
        file_path = INPUT_DIR / file_name

        if not file_path.exists():
            print(f"Warning: {file_path} does not exist. Skipped.")
            continue

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                merged_items.append(json.loads(line))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for item in merged_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Merged {len(merged_items)} entries into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()