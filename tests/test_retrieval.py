from src import retrieval


def _selection_for(question):
    return retrieval.chatbot_pipeline(question)["selection"]


def _faq_index(question):
    return next(
        index
        for index,item in enumerate(retrieval.qa_pairs)
        if item["question"] == question
    )


def test_exact_original_question_matches_itself():
    question="How to apply for school certificate via email?"

    selection=_selection_for(question)

    assert selection["matched_question"] == question
    assert selection["score"] > 0.9


def test_paraphrased_school_certificate_question_matches_expected_faq():
    selection=_selection_for("How can I get a school certificate by email?")

    assert selection["matched_question"] == "How to apply for school certificate via email?"
    assert "xmumac@xmu.edu.my" in selection["answer"]


def test_paraphrased_dormitory_fee_question_matches_expected_faq():
    selection=_selection_for("What are dormitory fees for D area?")

    assert selection["matched_question"] == (
        "What are the dormitory fees for D area and LY area respectively?"
    )
    assert "double room" in selection["answer"]


def test_keyword_missing_penalty_penalizes_candidates_without_keyword():
    query="What daily services can TNG eWallet be used for in Malaysia?"
    entities=retrieval.extract_entities(query)
    intent_info={
        "intent": "ask_definition",
        "score": 1.0,
        "is_rule_based": False,
        "response": None
    }

    features=retrieval.build_scoring_features(query,intent_info,entities)
    matching_index=_faq_index(query)
    unrelated_index=_faq_index("How to apply for school certificate via email?")

    assert retrieval.get_important_keyword(query) == "ewallet"
    assert features[matching_index][2] == 0.0
    assert features[unrelated_index][2] == -1.0


def test_unrelated_input_uses_fallback_without_crashing():
    selection=_selection_for("zzzz qwerty impossible nonsense")

    assert selection["matched_question"] is None
    assert selection["score"] < retrieval.FALLBACK_SCORE_THRESHOLD
    assert selection["answer"] == "Sorry, I do not have an answer for that."


def test_empty_input_uses_fallback_without_crashing():
    selection=_selection_for("")

    assert selection["matched_question"] is None
    assert selection["score"] < retrieval.FALLBACK_SCORE_THRESHOLD


def test_public_pipeline_shape_remains_compatible():
    result=retrieval.chatbot_pipeline("How can I get a school certificate by email?")

    assert set(result.keys()) == {"intent","entities","selection","response"}
    assert set(result["selection"].keys()) == {
        "answer",
        "score",
        "matched_question",
        "related_questions"
    }
    assert retrieval.get_response("How can I get a school certificate by email?") == result["response"]
