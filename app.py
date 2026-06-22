"""Web entry point for the XMUM freshman FAQ chatbot."""

from flask import Flask, jsonify, send_from_directory, request

from src.retrieval import chatbot_pipeline


app = Flask(__name__)


@app.get("/")
def index():
    return send_from_directory("ui", "index.html")


@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory("assets", filename)


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Please enter a question."}), 400
    if len(question) > 2000:
        return jsonify({"error": "Please keep your question under 2,000 characters."}), 400

    try:
        result = chatbot_pipeline(question.strip())
    except Exception:
        app.logger.exception("Chatbot pipeline failed")
        return jsonify({"error": "The chatbot could not answer right now."}), 500
    selection = result["selection"]
    return jsonify(
        {
            "answer": result["response"],
            "category": selection.get("category", "Unknown"),
            "confidence": round(float(selection["score"]), 4),
            "related_questions": selection.get("related_questions", []),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
