from flask import Flask, request, jsonify
from flask_cors import CORS
from core import load_mistral_llm, process_question
from config import DB_URI

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for frontend integration (Angular, Postman, etc.)

# Load Mistral model once at startup
llm = load_mistral_llm()

# Health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# Main chatbot endpoint
@app.route("/api/query", methods=["POST"])
def handle_query():
    try:
        data = request.get_json()

        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        question = data["question"].strip()
        if not question:
            return jsonify({"error": "Empty question"}), 400

        # Process question using Mistral + DB
        result = process_question(question, DB_URI, llm)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
