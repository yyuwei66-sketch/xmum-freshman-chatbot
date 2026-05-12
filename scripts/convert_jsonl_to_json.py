import json
from pathlib import Path

INPUT_FILE = Path("data/processed/faq_dataset.jsonl")
OUTPUT_FILE = Path("data/processed/faq_dataset.json")


def main():
    data = []

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            data.append(json.loads(line))

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Converted {len(data)} entries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()