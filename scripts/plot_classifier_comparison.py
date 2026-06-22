"""
Generate an English comparison figure for the three classification methods.

The figure combines:
1. Accuracy and macro-F1 comparison for Naive Bayes, Logistic Regression, and Linear SVM.
2. Training-time comparison.
3. Category-frequency distribution to make the long-tail pattern visible.

Default output:
    results/classifier_comparison_long_tail.svg
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPARISON = ROOT / "results" / "model_comparison.csv"
DEFAULT_DATASET = ROOT / "data" / "processed" / "faq_dataset.jsonl"
DEFAULT_REPORT = ROOT / "results" / "classification_report.txt"
DEFAULT_OUTPUT = ROOT / "results" / "classifier_comparison_long_tail.svg"


COLORS = {
    "Naive Bayes": "#2F80ED",
    "Logistic Regression": "#F2994A",
    "Linear SVM": "#27AE60",
    "accuracy": "#2563EB",
    "f1_macro": "#16A34A",
    "time": "#EA580C",
    "tail": "#6B7280",
    "grid": "#E5E7EB",
    "text": "#111827",
    "muted": "#6B7280",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_model_comparison(path: Path) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "model": row["model"],
                    "accuracy": float(row["accuracy"]),
                    "f1_macro": float(row["f1_macro"]),
                    "train_time": float(row["train_time"]),
                }
            )
    if not rows:
        raise ValueError(f"No model rows found in {path}")
    return rows


def load_dataset_counts(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    if not path.exists() or path.stat().st_size == 0:
        return counts

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
            category = item.get("category")
            if category:
                counts[str(category)] += 1
    return counts


def load_report_support(path: Path) -> Counter[str]:
    """Parse support values from sklearn classification_report text."""
    counts: Counter[str] = Counter()
    if not path.exists() or path.stat().st_size == 0:
        return counts

    line_re = re.compile(r"^\s*(?P<label>.+?)\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(?P<support>\d+)\s*$")
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = line_re.match(line.rstrip())
            if not match:
                continue
            label = match.group("label").strip()
            if label in {"accuracy", "macro avg", "weighted avg"}:
                continue
            counts[label] += int(match.group("support"))
    return counts


def text(x: float, y: float, value: object, size: int = 14, weight: str = "400",
         color: str = COLORS["text"], anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter, Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">'
        f"{esc(value)}</text>"
    )


def rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 4,
         stroke: str | None = None) -> str:
    stroke_attr = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{stroke_attr}/>'


def line(x1: float, y1: float, x2: float, y2: float, color: str = COLORS["grid"],
         width: float = 1, dash: str | None = None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width}"{dash_attr}/>'
    )


def metric_panel(rows: list[dict[str, float | str]], x: float, y: float, w: float, h: float) -> str:
    parts = [text(x, y - 16, "Model Quality: Accuracy vs. Macro-F1", 18, "700")]
    chart_x = x + 24
    chart_y = y + 20
    chart_w = w - 48
    chart_h = h - 100
    models = [str(r["model"]) for r in rows]
    group_w = chart_w / len(rows)
    bar_w = min(34, group_w * 0.22)

    for i in range(6):
        value = i / 5
        gy = chart_y + chart_h - value * chart_h
        parts.append(line(chart_x, gy, chart_x + chart_w, gy))
        parts.append(text(chart_x - 8, gy + 5, f"{value:.1f}", 11, color=COLORS["muted"], anchor="end"))

    parts.append(line(chart_x, chart_y, chart_x, chart_y + chart_h, "#9CA3AF"))
    parts.append(line(chart_x, chart_y + chart_h, chart_x + chart_w, chart_y + chart_h, "#9CA3AF"))

    for idx, row in enumerate(rows):
        gx = chart_x + idx * group_w + group_w / 2
        acc = float(row["accuracy"])
        f1 = float(row["f1_macro"])
        acc_h = acc * chart_h
        f1_h = f1 * chart_h
        parts.append(rect(gx - bar_w - 4, chart_y + chart_h - acc_h, bar_w, acc_h, COLORS["accuracy"]))
        parts.append(rect(gx + 4, chart_y + chart_h - f1_h, bar_w, f1_h, COLORS["f1_macro"]))
        parts.append(text(gx - bar_w / 2 - 4, chart_y + chart_h - acc_h - 6, f"{acc:.2f}", 11, "600", anchor="middle"))
        parts.append(text(gx + bar_w / 2 + 4, chart_y + chart_h - f1_h - 6, f"{f1:.2f}", 11, "600", anchor="middle"))
        parts.append(text(gx, chart_y + chart_h + 28, models[idx], 12, "600", anchor="middle"))

    legend_y = y + h - 14
    legend_x = x + w / 2 - 100
    parts.append(rect(legend_x, legend_y - 13, 12, 12, COLORS["accuracy"], 2))
    parts.append(text(legend_x + 18, legend_y - 3, "Accuracy", 12, color=COLORS["muted"]))
    parts.append(rect(legend_x + 110, legend_y - 13, 12, 12, COLORS["f1_macro"], 2))
    parts.append(text(legend_x + 128, legend_y - 3, "Macro-F1", 12, color=COLORS["muted"]))
    return "\n".join(parts)


def time_panel(rows: list[dict[str, float | str]], x: float, y: float, w: float, h: float) -> str:
    parts = [text(x, y - 16, "Training Time", 18, "700")]
    max_time = max(float(r["train_time"]) for r in rows) or 1.0
    bar_x = x + 170
    bar_w = w - 210
    row_h = (h - 32) / len(rows)

    for idx, row in enumerate(rows):
        cy = y + 22 + idx * row_h
        model = str(row["model"])
        train_time = float(row["train_time"])
        fill = COLORS.get(model, COLORS["time"])
        width = train_time / max_time * bar_w
        parts.append(text(x, cy + 17, model, 13, "600"))
        parts.append(rect(bar_x, cy, bar_w, 22, "#F3F4F6", 3))
        parts.append(rect(bar_x, cy, width, 22, fill, 3))
        value_x = min(bar_x + bar_w + 8, bar_x + width + 8)
        parts.append(text(value_x, cy + 16, f"{train_time:.4f}s", 12, "600"))
    parts.append(text(x, y + h - 2, "Shorter bars indicate faster training.", 12, color=COLORS["muted"]))
    return "\n".join(parts)


def long_tail_panel(counts: Counter[str], x: float, y: float, w: float, h: float, title: str) -> str:
    parts = [text(x, y - 16, title, 18, "700")]
    if not counts:
        parts.append(text(x, y + 40, "No category-count data found.", 14, color=COLORS["muted"]))
        return "\n".join(parts)

    items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    max_count = max(counts.values()) or 1
    total = sum(counts.values())
    label_w = 230
    bar_x = x + label_w
    bar_w = w - label_w - 72
    row_h = min(36, (h - 48) / len(items))
    y0 = y + 18

    for idx, (label, count) in enumerate(items):
        cy = y0 + idx * row_h
        width = count / max_count * bar_w
        color = "#374151" if idx < 3 else COLORS["tail"]
        parts.append(text(x, cy + 17, label, 12, "600" if idx < 3 else "400"))
        parts.append(rect(bar_x, cy, bar_w, 18, "#F3F4F6", 3))
        parts.append(rect(bar_x, cy, width, 18, color, 3))
        parts.append(text(bar_x + width + 8, cy + 14, count, 12, "600"))

    top_3 = sum(count for _, count in items[:3])
    tail_n = max(0, len(items) - 3)
    note = f"Top 3 categories: {top_3}/{total} samples ({top_3 / total:.1%}); remaining {tail_n} categories form the tail."
    parts.append(text(x, y + h - 8, note, 12, color=COLORS["muted"]))
    return "\n".join(parts)


def build_svg(
    rows: list[dict[str, float | str]],
    dataset_counts: Counter[str],
    report_counts: Counter[str],
) -> str:
    width = 1200
    height = 860
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        rect(0, 0, width, height, "#FFFFFF", 0),
        text(48, 54, "Classifier Comparison and Long-Tail Category Distribution", 28, "800"),
        text(48, 82, "Three classification methods are compared with quality metrics, training cost, and category imbalance.", 14, color=COLORS["muted"]),
        rect(36, 112, 690, 310, "#FFFFFF", 8, "#E5E7EB"),
        rect(754, 112, 410, 310, "#FFFFFF", 8, "#E5E7EB"),
        rect(36, 466, 1128, 330, "#FFFFFF", 8, "#E5E7EB"),
        metric_panel(rows, 66, 158, 630, 234),
        time_panel(rows, 784, 158, 350, 234),
    ]

    if dataset_counts:
        title = "Long-Tail Category Distribution in the Full FAQ Dataset"
        counts = dataset_counts
    else:
        title = "Long-Tail Category Distribution in the Test Set"
        counts = report_counts
    parts.append(long_tail_panel(counts, 66, 514, 1048, 240, title))

    if report_counts and dataset_counts:
        parts.append(text(66, 812, "Note: model metrics come from results/model_comparison.csv; long-tail bars use data/processed/faq_dataset.jsonl.", 12, color=COLORS["muted"]))
    elif report_counts:
        parts.append(text(66, 812, "Note: model metrics come from results/model_comparison.csv; long-tail bars use support values parsed from classification_report.txt.", 12, color=COLORS["muted"]))

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an English classifier comparison SVG.")
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON, help="Path to model_comparison.csv")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET, help="Path to FAQ JSONL dataset")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Path to sklearn classification_report.txt")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output SVG path")
    args = parser.parse_args()

    rows = load_model_comparison(args.comparison)
    dataset_counts = load_dataset_counts(args.dataset)
    report_counts = load_report_support(args.report)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_svg(rows, dataset_counts, report_counts), encoding="utf-8")
    print(f"Saved figure to {args.output}")


if __name__ == "__main__":
    main()
