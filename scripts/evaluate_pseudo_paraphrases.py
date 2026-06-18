"""Evaluate retrieval stability with deterministic pseudo paraphrases.

This is a weak, label-free retrieval check: each FAQ question is rewritten by a
small set of rules, and the expected match remains the original FAQ question.
It is not a substitute for human-labelled paraphrases, but it is useful for
spotting brittle scoring features.
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src import retrieval  # noqa: E402
from src.preprocessing import remove_stopwords, tokenize  # noqa: E402


SYNONYM_REPLACEMENTS = [
    (r"\bapply for\b", "request"),
    (r"\bapplication\b", "request"),
    (r"\bschool certificate\b", "school proof"),
    (r"\bcertificate\b", "proof document"),
    (r"\bdormitory\b", "hostel"),
    (r"\bdorm\b", "hostel"),
    (r"\bfees\b", "charges"),
    (r"\bfee\b", "charge"),
    (r"\bemail\b", "e-mail"),
    (r"\btransportation\b", "transport"),
    (r"\bbus\b", "shuttle"),
    (r"\btuition\b", "study fee"),
    (r"\bpayment\b", "paying"),
    (r"\bregister\b", "sign up"),
    (r"\bregistration\b", "sign-up"),
    (r"\bwhere\b", "which place"),
    (r"\bhow much\b", "what is the cost"),
]

LEAD_IN_PATTERNS = [
    ("polite_prefix", "Could you tell me {body}?"),
    ("need_to_know", "I need to know {body}."),
]


def clean_body(question: str) -> str:
    body = question.strip()
    body = re.sub(r"\s+", " ", body)
    body = body.rstrip("?.!")
    if body:
        body = body[0].lower() + body[1:]
    return body


def replace_question_starter(question: str) -> str | None:
    replacements = [
        (r"^how to\b", "how can I"),
        (r"^how do i\b", "what is the way to"),
        (r"^what are\b", "can you tell me the"),
        (r"^what is\b", "could you explain"),
        (r"^where can i\b", "which place lets me"),
        (r"^when\b", "at what time"),
    ]
    for pattern, replacement in replacements:
        rewritten = re.sub(pattern, replacement, question, flags=re.IGNORECASE)
        if rewritten != question:
            return rewritten
    return None


def synonym_swap(question: str) -> str | None:
    rewritten = question
    for pattern, replacement in SYNONYM_REPLACEMENTS:
        rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
    return rewritten if rewritten != question else None


def keyword_only(question: str) -> str | None:
    tokens = remove_stopwords(tokenize(question))
    if len(tokens) < 3:
        return None
    return " ".join(tokens[:8]) + "?"


def reverse_chunks(question: str) -> str | None:
    body = clean_body(question)
    chunks = re.split(r"\b(?:for|of|in|via|with|to)\b", body, maxsplit=1)
    if len(chunks) != 2:
        return None
    left = chunks[0].strip(" ,")
    right = chunks[1].strip(" ,")
    if not left or not right:
        return None
    return f"{right}: {left}?"


def generate_variants(question: str) -> list[tuple[str, str]]:
    body = clean_body(question)
    variants: list[tuple[str, str]] = []

    for name, template in LEAD_IN_PATTERNS:
        variants.append((name, template.format(body=body)))

    starter = replace_question_starter(question)
    if starter:
        variants.append(("starter_replace", starter))

    synonyms = synonym_swap(question)
    if synonyms:
        variants.append(("synonym_swap", synonyms))

    keywords = keyword_only(question)
    if keywords:
        variants.append(("keyword_only", keywords))

    reversed_question = reverse_chunks(question)
    if reversed_question:
        variants.append(("reverse_chunks", reversed_question))

    deduped = []
    seen = {question.strip().lower()}
    for name, variant in variants:
        normalized = variant.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped.append((name, variant))
    return deduped


def evaluate(limit: int | None, seed: int) -> tuple[dict[str, dict[str, float]], list[dict[str, object]]]:
    rng = random.Random(seed)
    indexed_questions = list(enumerate(retrieval.questions))
    if limit is not None and limit < len(indexed_questions):
        indexed_questions = rng.sample(indexed_questions, limit)

    stats = defaultdict(lambda: {
        "total": 0,
        "top1": 0,
        "top4": 0,
        "fallback": 0,
        "score_sum": 0.0,
        "skipped_rule": 0,
    })
    failures = []

    for expected_index, expected_question in indexed_questions:
        for variant_type, query in generate_variants(expected_question):
            result = retrieval.chatbot_pipeline(query)
            if result["intent"]["is_rule_based"]:
                stats[variant_type]["skipped_rule"] += 1
                continue

            selection = result["selection"]
            matched = selection["matched_question"]
            related = selection["related_questions"]
            score = float(selection["score"])

            row = stats[variant_type]
            row["total"] += 1
            row["score_sum"] += score
            if matched == expected_question:
                row["top1"] += 1
            if matched == expected_question or expected_question in related:
                row["top4"] += 1
            if matched is None:
                row["fallback"] += 1

            if matched != expected_question:
                failures.append({
                    "variant_type": variant_type,
                    "query": query,
                    "expected_index": expected_index,
                    "expected": expected_question,
                    "matched": matched,
                    "score": score,
                    "related_contains_expected": expected_question in related,
                })

    stats["overall"] = {
        key: sum(row[key] for row in stats.values())
        for key in ["total", "top1", "top4", "fallback", "score_sum"]
    }
    stats["overall"]["skipped_rule"] = sum(
        row["skipped_rule"]
        for name, row in stats.items()
        if name != "overall"
    )
    return stats, failures


def print_report(stats: dict[str, dict[str, float]], failures: list[dict[str, object]], max_failures: int) -> None:
    print("Pseudo paraphrase retrieval stability")
    print(f"FAQ count: {len(retrieval.qa_pairs)}")
    print()
    print(f"{'variant':<18} {'n':>5} {'skipped':>8} {'top1':>8} {'top4':>8} {'fallback':>9} {'avg_score':>10}")
    print("-" * 74)

    ordered_names = ["overall"] + sorted(name for name in stats if name != "overall")
    for name in ordered_names:
        row = stats[name]
        total = row["total"]
        if total == 0:
            continue
        print(
            f"{name:<18} {int(total):>5} "
            f"{int(row['skipped_rule']):>8} "
            f"{row['top1'] / total:>8.3f} "
            f"{row['top4'] / total:>8.3f} "
            f"{row['fallback'] / total:>9.3f} "
            f"{row['score_sum'] / total:>10.3f}"
        )

    print()
    print(f"Failures shown: {min(max_failures, len(failures))} / {len(failures)}")
    for failure in failures[:max_failures]:
        print("-" * 64)
        print(f"type: {failure['variant_type']} score: {failure['score']:.3f}")
        print(f"query: {failure['query']}")
        print(f"expected: {failure['expected']}")
        print(f"matched: {failure['matched']}")
        print(f"expected in related: {failure['related_contains_expected']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Number of FAQ questions to sample.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-failures", type=int, default=12)
    args = parser.parse_args()

    stats, failures = evaluate(args.limit, args.seed)
    print_report(stats, failures, args.max_failures)


if __name__ == "__main__":
    main()
