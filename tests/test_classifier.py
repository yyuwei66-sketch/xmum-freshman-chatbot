import sys
import pytest
import numpy as np
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
 
from classifier import (
    load_dataset,
    predict,
    predict_proba,
    predict_top_n,
    build_naive_bayes_pipeline,
    build_logistic_pipeline,
    build_svm_pipeline,
    NaiveBayes,
    DATA_PATH,
    MODEL_PATH,
)
 
EXPECTED_CATEGORIES = {
    "Academic Affairs",
    "University Platforms & IT Support",
    "Registration & Orientation",
    "Campus Services",
    "Accommodation & Living",
    "Transportation",
    "Finance & Fees",
}

 
@pytest.fixture(scope="module")
def mini_data():
    X = [
        # Finance & Fees (×2)
        "pay fee tuition semester",
        "fee payment finance deadline",
        # IT Support (×2)
        "wifi connect network portal",
        "it support login reset password",
        # Accommodation (×2)
        "book room dormitory stay",
        "hostel accommodation living",
        # Transportation (×2)
        "bus shuttle transport route",
        "campus transport schedule",
        # Registration (×2)
        "register course enrol orientation",
        "course registration semester enrol",
        # Academic Affairs (×2)
        "appeal result grade academic",
        "exam appeal academic result",
        # Campus Services (×2)
        "campus facility sport clinic",
        "campus service library cafeteria",
    ]
    y = [
        "Finance & Fees",
        "Finance & Fees",
        "University Platforms & IT Support",
        "University Platforms & IT Support",
        "Accommodation & Living",
        "Accommodation & Living",
        "Transportation",
        "Transportation",
        "Registration & Orientation",
        "Registration & Orientation",
        "Academic Affairs",
        "Academic Affairs",
        "Campus Services",
        "Campus Services",
    ]
    return X, y
 
 
# 1. Dataset loading
class TestLoadDataset:
 
    def test_loads_successfully(self):
        df = load_dataset(DATA_PATH)
        assert len(df) > 0
 
    def test_required_columns_exist(self):
        df = load_dataset(DATA_PATH)
        for col in ["question", "category", "text"]:
            assert col in df.columns
 
    def test_no_null_text(self):
        df = load_dataset(DATA_PATH)
        assert df["text"].isnull().sum() == 0
 
    def test_no_null_category(self):
        df = load_dataset(DATA_PATH)
        assert df["category"].isnull().sum() == 0
 
    def test_expected_categories_present(self):
        df = load_dataset(DATA_PATH)
        assert set(df["category"].unique()) == EXPECTED_CATEGORIES
 
    def test_text_is_preprocessed(self):
        df = load_dataset(DATA_PATH)
        sample = df["text"].iloc[0]
        assert sample == sample.lower()
        assert "?" not in sample
 
 
# 2.NaiveBayes
class TestNaiveBayes:
 
    @pytest.fixture
    def trained_nb(self):
        X = [
            "register course semester",
            "academic appeal result",
            "pay tuition fee deadline",
            "fee payment finance",
            "wifi connect campus network",
            "it support login portal",
        ]
        y = [
            "Academic Affairs",
            "Academic Affairs",
            "Finance & Fees",
            "Finance & Fees",
            "University Platforms & IT Support",
            "University Platforms & IT Support",
        ]
        nb = NaiveBayes()
        nb.fit(X, y)
        return nb
 
    def test_fit_stores_classes(self, trained_nb):
        assert set(trained_nb.classes_) == {
            "Academic Affairs", "Finance & Fees",
            "University Platforms & IT Support",
        }
 
    def test_predict_returns_known_class(self, trained_nb):
        assert trained_nb.predict(["pay fee tuition"])[0] in trained_nb.classes_
 
    def test_predict_correct_finance(self, trained_nb):
        assert trained_nb.predict(["pay fee tuition"])[0] == "Finance & Fees"
 
    def test_predict_correct_it(self, trained_nb):
        assert trained_nb.predict(["wifi connect"])[0] == "University Platforms & IT Support"
 
    def test_predict_proba_sums_to_one(self, trained_nb):
        proba = trained_nb.predict_proba(["some query"])
        assert abs(proba[0].sum() - 1.0) < 1e-6
 
    def test_predict_proba_shape(self, trained_nb):
        proba = trained_nb.predict_proba(["q1", "q2"])
        assert proba.shape == (2, len(trained_nb.classes_))
 
    def test_laplace_smoothing_unseen_word(self, trained_nb):
        """Unseen vocab should not crash and proba should still sum to 1."""
        proba = trained_nb.predict_proba(["xyzunknown999"])
        assert proba[0].sum() > 0
        assert abs(proba[0].sum() - 1.0) < 1e-6
 
    def test_log_prior_paper_formula(self, trained_nb):
        """P(c) = Nc/N  →  log P(Academic Affairs) = log(2/6)"""
        import math
        expected = math.log(2 / 6)
        assert abs(trained_nb.log_prior_["Academic Affairs"] - expected) < 1e-9
 
 
# 3. predict()
class TestPredict:
 
    def test_returns_string(self):
        assert isinstance(predict("How do I pay my tuition fees?"), str)
 
    def test_returns_known_category(self):
        assert predict("How do I pay my tuition fees?") in EXPECTED_CATEGORIES
 
    def test_finance_query(self):
        assert predict("What is the deadline to pay my tuition?") == "Finance & Fees"
 
    def test_it_query(self):
        assert predict("How do I connect to the campus WiFi?") == "University Platforms & IT Support"
 
    def test_accommodation_query(self):
        assert predict("How do I book a dormitory room?") == "Accommodation & Living"
 
    def test_empty_string_no_crash(self):
        result = predict("")
        assert isinstance(result, str)
 
    def test_short_input(self):
        assert isinstance(predict("hi"), str)
 
    def test_numeric_input(self):
        assert isinstance(predict("12345"), str)
 
    def test_consistent(self):
        q = "Where can I get my student card?"
        assert predict(q) == predict(q)
 
 
# 4. predict_proba()
class TestPredictProba:
 
    def test_returns_dict(self):
        assert isinstance(predict_proba("How do I pay fees?"), dict)
 
    def test_all_categories_present(self):
        assert set(predict_proba("How do I pay fees?").keys()) == EXPECTED_CATEGORIES
 
    def test_proba_sum_to_one(self):
        total = sum(predict_proba("How do I pay fees?").values())
        assert abs(total - 1.0) < 1e-4
 
    def test_sorted_descending(self):
        vals = list(predict_proba("How do I pay fees?").values())
        assert vals == sorted(vals, reverse=True)
 
    def test_top_matches_predict(self):
        q = "What is the fee structure?"
        assert list(predict_proba(q).keys())[0] == predict(q)
 
    def test_empty_string_no_crash(self):
        r = predict_proba("")
        assert abs(sum(r.values()) - 1.0) < 1e-4
 
 
# 5. predict_top_n()
class TestPredictTopN:
 
    def test_returns_list(self):
        assert isinstance(predict_top_n("campus bus route", n=3), list)
 
    def test_correct_length(self):
        for n in [1, 2, 3]:
            assert len(predict_top_n("some query", n=n)) == n
 
    def test_item_has_keys(self):
        for item in predict_top_n("pay fees", n=3):
            assert "category" in item and "probability" in item
 
    def test_item_types(self):
        for item in predict_top_n("pay fees", n=3):
            assert isinstance(item["category"], str)
            assert isinstance(item["probability"], float)
 
    def test_valid_categories(self):
        for item in predict_top_n("register course", n=3):
            assert item["category"] in EXPECTED_CATEGORIES
 
    def test_sorted_descending(self):
        probs = [i["probability"] for i in predict_top_n("some query", n=3)]
        assert probs == sorted(probs, reverse=True)
 
    def test_n1_matches_predict(self):
        q = "wifi password reset"
        assert predict_top_n(q, n=1)[0]["category"] == predict(q)
 
    def test_default_n_is_3(self):
        assert len(predict_top_n("campus query")) == 3
 

# 6. Pipeline builders
class TestPipelineBuilders:
 
    def test_naive_bayes_fits(self, mini_data):
        X, y = mini_data
        p = build_naive_bayes_pipeline()
        p.fit(X, y)
        assert len(p.predict(X)) == len(X)
 
    def test_logistic_fits(self, mini_data):
        X, y = mini_data
        p = build_logistic_pipeline()
        p.fit(X, y)
        assert len(p.predict(X)) == len(X)
 
    def test_svm_fits(self, mini_data):
        """SVM uses CalibratedClassifierCV — needs cv=2 for small datasets."""
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.svm import LinearSVC
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import Pipeline
        X, y = mini_data
        p = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("clf",   CalibratedClassifierCV(
                          LinearSVC(max_iter=2000, random_state=42), cv=2)),
        ])
        p.fit(X, y)
        assert len(p.predict(X)) == len(X)
 
    def test_nb_has_predict_proba(self, mini_data):
        X, y = mini_data
        p = build_naive_bayes_pipeline()
        p.fit(X, y)
        proba = p.predict_proba(X[:1])
        assert proba.shape[1] == len(set(y))
 
    def test_logistic_has_predict_proba(self, mini_data):
        X, y = mini_data
        p = build_logistic_pipeline()
        p.fit(X, y)
        proba = p.predict_proba(X[:1])
        assert proba.shape[1] == len(set(y))
 
 
# 7. Model file on disk
class TestModelFile:
 
    def test_model_file_exists(self):
        assert MODEL_PATH.exists(), (
            f"Model not found at {MODEL_PATH}. Run: python src/classifier.py"
        )
 
    def test_model_loadable(self):
        import joblib
        pipeline = joblib.load(MODEL_PATH)
        assert hasattr(pipeline, "predict")
        assert hasattr(pipeline, "predict_proba")
 
    def test_loaded_model_predicts(self):
        import joblib
        pipeline = joblib.load(MODEL_PATH)
        pred = pipeline.predict(["pay tuition deadline"])
        assert pred[0] in EXPECTED_CATEGORIES