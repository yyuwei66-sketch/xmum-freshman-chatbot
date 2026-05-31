import json, time, math, warnings, joblib
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, ClassifierMixin
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocessing import preprocess_text

warnings.filterwarnings("ignore")
ROOT         = Path(__file__).resolve().parent.parent
DATA_PATH    = ROOT / "data" / "processed" / "faq_dataset.jsonl"
MODELS_DIR   = ROOT / "models"
RESULTS_DIR  = ROOT / "results"
MODEL_PATH   = MODELS_DIR / "category_classifier.pkl"
REPORT_PATH  = RESULTS_DIR / "classification_report.txt"
COMPARE_PATH = RESULTS_DIR / "model_comparison.csv"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

#Dataset
def load_dataset(path=DATA_PATH):
    records = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    df = pd.DataFrame(records)[["question", "category", "keywords"]].dropna(
        subset=["question", "category"])
    def build(row):
        kw = " ".join(row["keywords"]) if isinstance(row["keywords"], list) else ""
        return preprocess_text(row["question"] + " " + kw)
    df["text"] = df.apply(build, axis=1)
    return df

#Naive Bayes
class NaiveBayes(BaseEstimator, ClassifierMixin):
    """
    P(c)   = Nc / N
    P(w|c) = (count(w,c)+1) / (Nwords_c + |V|)   [Laplace smoothing]
    """
    def fit(self, X, y):
        X = list(X)
        self.classes_ = np.unique(y)
        N = len(y)
        vocab = set(w for doc in X for w in doc.split())
        self.vocab_ = vocab
        V = len(vocab)
        self.log_prior_, self.log_likelihood_ = {}, {}
        for c in self.classes_:
            docs_c = [X[i] for i in range(len(X)) if y[i] == c]
            Nc = len(docs_c)
            self.log_prior_[c] = math.log(Nc / N)
            wc = Counter(w for doc in docs_c for w in doc.split())
            Nw = sum(wc.values())
            self.log_likelihood_[c] = {
                w: math.log((wc.get(w, 0) + 1) / (Nw + V)) for w in vocab
            }
            self.log_likelihood_[c]["__Nw__"] = Nw
            self.log_likelihood_[c]["__V__"]  = V
        return self
 
    def _score(self, doc, c):
        ll = self.log_likelihood_[c]
        Nw, V = ll["__Nw__"], ll["__V__"]
        return self.log_prior_[c] + sum(
            ll.get(w, math.log(1 / (Nw + V))) for w in doc.split()
        )
 
    def predict(self, X):
        return np.array([max(self.classes_,
                             key=lambda c: self._score(d, c)) for d in X])
 
    def predict_proba(self, X):
        rows = []
        for doc in X:
            scores = np.array([self._score(doc, c) for c in self.classes_])
            scores -= scores.max()
            e = np.exp(scores)
            rows.append(e / e.sum())
        return np.array(rows)
 
    # sklearn Pipeline compatibility — NB works directly on strings
    def transform(self, X): return X

#Pipeline builders
def _tfidf():
    return TfidfVectorizer(ngram_range=(1,2), max_features=5000,
                           sublinear_tf=True, strip_accents="unicode")

class IdentityTransformer(BaseEstimator):
    def fit(self, X, y=None): return self
    def transform(self, X):   return list(X)
    def fit_transform(self, X, y=None): return list(X)

def build_naive_bayes_pipeline():
    return Pipeline([("id", IdentityTransformer()), ("clf", NaiveBayes())])

def build_logistic_pipeline():
    return Pipeline([("tfidf", _tfidf()),
                     ("clf",   LogisticRegression(max_iter=1000, C=1.0,
                                                   solver="lbfgs", random_state=42))])
 
def build_svm_pipeline(cv=5):
    return Pipeline([("tfidf", _tfidf()),
                     ("clf",   CalibratedClassifierCV(
                                   LinearSVC(max_iter=2000, C=1.0,
                                             random_state=42), cv=cv))])

#Evaluate
def evaluate_pipeline(pipeline, X_train, X_test, y_train, y_test, name):
    t0 = time.time()
    pipeline.fit(list(X_train), list(y_train))
    t = round(time.time() - t0, 4)
    yp = pipeline.predict(list(X_test))
    return {"model": name,
            "accuracy":   round(accuracy_score(y_test, yp), 4),
            "f1_macro":   round(f1_score(y_test, yp, average="macro",
                                         zero_division=0), 4),
            "train_time": t, "pipeline": pipeline, "y_pred": yp}

#Full training workflow
def train_and_compare(data_path=DATA_PATH):
    print("=" * 60)
    print("ML Classification Training")
    print("=" * 60)
    df = load_dataset(data_path)
    print(f"Dataset: {len(df)} samples")
    print(df["category"].value_counts().to_string())
 
    X, y = df["text"].values, df["category"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")
 
    models = {"Naive Bayes": build_naive_bayes_pipeline(),
              "Logistic Regression":         build_logistic_pipeline(),
              "Linear SVM":                  build_svm_pipeline()}
 
    results = []
    for name, pipe in models.items():
        print(f"\nTraining {name} ...", end="  ")
        r = evaluate_pipeline(pipe, X_train, X_test, y_train, y_test, name)
        results.append(r)
        print(f"acc={r['accuracy']:.4f}  f1={r['f1_macro']:.4f}  ({r['train_time']}s)")
 
    best = max(results, key=lambda r: r["f1_macro"])
    print(f"\nBest: {best['model']}  acc={best['accuracy']:.4f}  f1={best['f1_macro']:.4f}")
    joblib.dump(best["pipeline"], MODEL_PATH)
    print(f"Saved → {MODEL_PATH}")
 
    report = classification_report(y_test, best["y_pred"], digits=4, zero_division=0)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(f"Best model: {best['model']}\n{'='*60}\n{report}\n\n")
        f.write("Comparison\n" + "="*60 + "\n")
        for r in results:
            m = " ← best" if r["model"] == best["model"] else ""
            f.write(f"{r['model']:30s} acc={r['accuracy']:.4f}  f1={r['f1_macro']:.4f}{m}\n")
    print(f"Report → {REPORT_PATH}")
 
    pd.DataFrame([{"model":r["model"],"accuracy":r["accuracy"],
                   "f1_macro":r["f1_macro"],"train_time":r["train_time"]}
                  for r in results]).to_csv(COMPARE_PATH, index=False)
    print(f"CSV    → {COMPARE_PATH}")
    return best["pipeline"]

#Lazy-loaded inference pipeline
_pipeline = None
def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        if not MODEL_PATH.exists():
            train_and_compare()
        _pipeline = joblib.load(MODEL_PATH)
    return _pipeline

#Public API
def predict(text: str) -> str:
    """Predict FAQ category. Preprocessing applied internally."""
    p = preprocess_text(text)
    return _get_pipeline().predict([p])[0]

def predict_proba(text: str) -> dict:
    """Return {category: probability} sorted descending. For Member 5."""
    p    = preprocess_text(text)
    pipe = _get_pipeline()
    prob = pipe.predict_proba([p])[0]
    res  = {str(k): float(v) for k, v in zip(pipe.classes_, prob.round(4))}
    return dict(sorted(res.items(), key=lambda x: x[1], reverse=True))

def predict_top_n(text: str, n: int = 3) -> list:
    """Return top-N [{category, probability}]. For Member 5 medium-confidence."""
    return [{"category": c, "probability": float(p)}
            for c, p in list(predict_proba(text).items())[:n]]

if __name__ == "__main__":
    train_and_compare()
    print("\n--- Smoke Test ---")
    for q, exp in [
        ("How do I appeal my exam results?",          "Academic Affairs"),
        ("Where can I park my motorcycle on campus?", "Campus Services"),
        ("What is the deadline to pay my tuition?",   "Finance & Fees"),
        ("How do I connect to the campus WiFi?",      "University Platforms & IT Support"),
        ("Is there a shuttle bus to KL Sentral?",     "Transportation"),
        ("How do I book a dormitory room?",           "Accommodation & Living"),
    ]:
        top1 = predict(q)
        conf = predict_top_n(q, 1)[0]["probability"]
        ok   = "OK" if top1 == exp else "MISS"
        print(f"  [{ok}] {q[:52]:<52s} → {top1:<35s} conf={conf:.2f}")