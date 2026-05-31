import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score,
    classification_report, confusion_matrix
)

from classifier import (
    load_dataset,
    build_naive_bayes_pipeline,
    build_logistic_pipeline,
    build_svm_pipeline,
    evaluate_pipeline,
    DATA_PATH, RESULTS_DIR,
)

COMPARE_PATH = RESULTS_DIR / "model_comparison.csv"
REPORT_PATH  = RESULTS_DIR / "classification_report.txt"

def run_comparison(data_path=DATA_PATH, test_size=0.2, random_state=42) -> pd.DataFrame:
    """
    Train all three models on the FAQ dataset and compare performance.
 
    Returns
    -------
    pd.DataFrame
        Columns: model, accuracy, f1_macro, train_time
        Sorted by f1_macro descending.
    """
    print("=" * 60)
    print("Model Comparison — Naive Bayes vs LR vs Linear SVM")
    print("=" * 60)

    # Load & split
    df = load_dataset(data_path)
    X, y = df["text"].values, df["category"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"Train: {len(X_train)}  |  Test: {len(X_test)}\n")

    models = {
        "Naive Bayes": build_naive_bayes_pipeline(),
        "Logistic Regression":         build_logistic_pipeline(),
        "Linear SVM":                  build_svm_pipeline(),
    }

    results = []
    detail_reports = []

    for name, pipeline in models.items():
        print(f"Training {name} ...", end="  ")
        r = evaluate_pipeline(pipeline, X_train, X_test, y_train, y_test, name)
        results.append(r)
 
        per_class = classification_report(
            y_test, r["y_pred"], digits=4, zero_division=0
        )
        detail_reports.append((name, r["accuracy"], r["f1_macro"], per_class))
        print(f"acc={r['accuracy']:.4f}  f1={r['f1_macro']:.4f}  ({r['train_time']}s)")

    # Sort by F1-macro
    results.sort(key=lambda r: r["f1_macro"], reverse=True)
    best = results[0]

    #Print summary table
    print("\n" + "-" * 60)
    print(f"{'Model':<32} {'Accuracy':>10} {'F1-macro':>10} {'Time(s)':>9}")
    print("-" * 60)
    for r in results:
        mark = " ←" if r["model"] == best["model"] else ""
        print(f"{r['model']:<32} {r['accuracy']:>10.4f} {r['f1_macro']:>10.4f} "
              f"{r['train_time']:>9}{mark}")
    print("-" * 60)
    print(f"Best: {best['model']}")

    df_out = pd.DataFrame([
        {
            "model":      r["model"],
            "accuracy":   r["accuracy"],
            "f1_macro":   r["f1_macro"],
            "train_time": r["train_time"],
        }
        for r in results
    ])
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(COMPARE_PATH, index=False)
    print(f"\nSaved → {COMPARE_PATH}")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("Model Comparison Report\n")
        f.write("=" * 60 + "\n\n")

        # Summary table
        f.write(f"{'Model':<32} {'Accuracy':>10} {'F1-macro':>10} {'Time(s)':>9}\n")
        f.write("-" * 60 + "\n")
        for r in results:
            mark = " ← best" if r["model"] == best["model"] else ""
            f.write(f"{r['model']:<32} {r['accuracy']:>10.4f} {r['f1_macro']:>10.4f} "
                    f"{r['train_time']:>9}{mark}\n")
        f.write("\n\n")

        # Per-class detail for each model
        for name, acc, f1, report in detail_reports:
            f.write(f"{'=' * 60}\n")
            f.write(f"Detailed Report — {name}\n")
            f.write(f"Accuracy: {acc:.4f}  |  F1-macro: {f1:.4f}\n")
            f.write("-" * 60 + "\n")
            f.write(report + "\n\n")

    print(f"Saved → {REPORT_PATH}")
    return df_out


if __name__ == "__main__":
    run_comparison()
 