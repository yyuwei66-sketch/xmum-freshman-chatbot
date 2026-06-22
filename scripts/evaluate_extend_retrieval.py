"""Evaluate retrieval precision using labelled queries from extend_data.jsonl."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src import retrieval  # noqa: E402


def _safe_rate(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _question_to_id() -> dict[str, str]:
    return {
        item["question"]: item["id"]
        for item in retrieval.qa_pairs
        if item.get("question") and item.get("id")
    }


def evaluate(extend_path: Path) -> tuple[dict[str, dict[str, float]], list[dict[str, object]], list[str]]:
    faq_by_id = {item.get("id"): item for item in retrieval.qa_pairs}
    id_by_question = _question_to_id()

    stats = defaultdict(lambda: {
        "n": 0,
        "top1": 0,
        "top4": 0,
        "fallback": 0,
        "score_sum": 0.0,
    })
    failures: list[dict[str, object]] = []
    missing_ids: list[str] = []

    for line in extend_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        record = json.loads(line)
        expected_id = record["id"]
        expected = faq_by_id.get(expected_id)
        if expected is None:
            missing_ids.append(expected_id)
            continue

        for query_type, query in record["queries"].items():
            result = retrieval.chatbot_pipeline(query)
            selection = result["selection"]
            matched_question = selection["matched_question"]
            matched_id = id_by_question.get(matched_question)
            related_ids = [
                id_by_question[question]
                for question in selection["related_questions"]
                if question in id_by_question
            ]

            is_top1 = matched_id == expected_id
            is_top4 = is_top1 or expected_id in related_ids
            score = float(selection["score"])

            row = stats[query_type]
            row["n"] += 1
            row["top1"] += int(is_top1)
            row["top4"] += int(is_top4)
            row["fallback"] += int(matched_id is None)
            row["score_sum"] += score

            if not is_top1:
                failures.append({
                    "id": expected_id,
                    "type": query_type,
                    "query": query,
                    "expected": expected["question"],
                    "matched_id": matched_id,
                    "matched": matched_question,
                    "related_ids": related_ids,
                    "score": score,
                    "top4": is_top4,
                })

    overall = {
        "n": sum(row["n"] for row in stats.values()),
        "top1": sum(row["top1"] for row in stats.values()),
        "top4": sum(row["top4"] for row in stats.values()),
        "fallback": sum(row["fallback"] for row in stats.values()),
        "score_sum": sum(row["score_sum"] for row in stats.values()),
    }
    stats["overall"] = overall
    return stats, failures, missing_ids


def print_report(
    stats: dict[str, dict[str, float]],
    failures: list[dict[str, object]],
    missing_ids: list[str],
    max_failures: int,
) -> None:
    print("Extend-data retrieval precision")
    print(f"FAQ indexed: {len(retrieval.qa_pairs)}")
    print(f"Queries evaluated: {int(stats['overall']['n'])}")
    print(f"Missing ids: {len(missing_ids)}")
    if missing_ids:
        print("Missing id sample:", ", ".join(missing_ids[:20]))
    print()
    print(f"{'type':<12} {'n':>5} {'top1':>8} {'top4':>8} {'fallback':>9} {'avg_score':>10}")
    print("-" * 58)

    for name in ["overall", *sorted(key for key in stats if key != "overall")]:
        row = stats[name]
        total = row["n"]
        print(
            f"{name:<12} {int(total):>5} "
            f"{_safe_rate(row['top1'], total):>8.3f} "
            f"{_safe_rate(row['top4'], total):>8.3f} "
            f"{_safe_rate(row['fallback'], total):>9.3f} "
            f"{_safe_rate(row['score_sum'], total):>10.3f}"
        )

    print()
    print(f"Top1 failures shown: {min(max_failures, len(failures))} / {len(failures)}")
    for failure in failures[:max_failures]:
        print("-" * 72)
        print(
            f"id={failure['id']} type={failure['type']} "
            f"score={failure['score']:.3f} top4={failure['top4']}"
        )
        print(f"query: {failure['query']}")
        print(f"expected: {failure['expected']}")
        print(f"matched_id: {failure['matched_id']}")
        print(f"matched: {failure['matched']}")
        print(f"related_ids: {failure['related_ids']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--extend-path",
        type=Path,
        default=ROOT_DIR / "data" / "train&test" / "extend_data.jsonl",
    )
    parser.add_argument("--max-failures", type=int, default=25)
    args = parser.parse_args()

    stats, failures, missing_ids = evaluate(args.extend_path)
    print_report(stats, failures, missing_ids, args.max_failures)


if __name__ == "__main__":
    main()
