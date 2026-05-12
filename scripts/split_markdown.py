from pathlib import Path
import re
import json

RAW_DIR = Path("data/raw/handbooks")
OUTPUT_FILE = Path("data/chunks/all_chunks.jsonl")


def split_markdown_by_headings(text):
    pattern = r"(?=^#{1,4}\s+)"
    chunks = re.split(pattern, text, flags=re.MULTILINE)

    results = []

    for chunk in chunks:
        chunk = chunk.strip()

        if len(chunk) < 100:
            continue

        lines = chunk.splitlines()
        title = lines[0].strip()
        title = re.sub(r"^#{1,4}\s*", "", title)

        results.append({
            "title": title,
            "content": chunk
        })

    return results


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    chunk_counter = 1

    md_files = sorted(RAW_DIR.glob("*.md"))

    if not md_files:
        print("No markdown files found in data/raw/handbooks/")
        return

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        chunks = split_markdown_by_headings(text)

        for chunk in chunks:
            item = {
                "chunk_id": f"CHUNK_{chunk_counter:04d}",
                "handbook": md_file.name,
                "title": chunk["title"],
                "content": chunk["content"]
            }
            all_chunks.append(item)
            chunk_counter += 1

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for item in all_chunks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Saved {len(all_chunks)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()