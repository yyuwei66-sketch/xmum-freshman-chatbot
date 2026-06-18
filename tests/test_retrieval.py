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


def test_keyword_token_similarity_scores_related_candidate_higher():
    query="What daily services can TNG eWallet be used for in Malaysia?"
    important_keyword=retrieval.get_important_keyword(query)
    keyword_similarities=retrieval.keyword_token_similarities(important_keyword)
    matching_index=_faq_index(query)
    unrelated_index=_faq_index("How to apply for school certificate via email?")

    assert important_keyword == "ewallet"
    assert keyword_similarities[matching_index] > keyword_similarities[unrelated_index]


def test_keyword_similarity_breaks_close_rrf_ties():
    high_keyword=(0.505,0.9,0.8,1)
    low_keyword=(0.500,0.1,0.9,2)

    assert retrieval.score_sort_key(high_keyword) > retrieval.score_sort_key(low_keyword)


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
