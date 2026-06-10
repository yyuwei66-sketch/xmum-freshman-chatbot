HIGH_THRESHOLD = 0.75
MEDIUM_THRESHOLD = 0.50

def get_confidence_level(score):
    """Return confidence level: HIGH / MEDIUM / LOW"""
    if score >= HIGH_THRESHOLD:
        return "HIGH"
    elif score >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    else:
        return "LOW"

def format_related_questions(related_questions, max_questions=3):
    """Format top related questions into a readable list"""
    if not related_questions:
        return ""
    
    questions = related_questions[:max_questions]
    return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

def generate_response(
    score,
    direct_answer,
    related_questions,
    fallback_response="Sorry, I cannot answer this question. Please try another."):

    # Generate final response based on confidence score:
    # HIGH: Direct answer
    # MEDIUM: Answer + Top-3 suggestions
    # LOW: Fallback + Top-3 suggestions

    level = get_confidence_level(score)

    if level == "HIGH":
        response = direct_answer if direct_answer else fallback_response

    elif level == "MEDIUM":
        related_text = format_related_questions(related_questions)
        response = (
            f"{direct_answer}\n\n"
            f"You may also want to know:\n"
            f"{related_text}"
        )

    else:
        related_text = format_related_questions(related_questions)
        response = (
            f"{fallback_response}\n\n"
            f"Recommended Related Questions:\n"
            f"{related_text}"
        )

    return {
        "confidence_score": round(score, 4),
        "confidence_level": level,
        "response": response
    }
