import os
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

# Initialize Groq client
client = Groq(api_key=API_KEY)

# ✅ Latest supported model (fast and reliable)
MODEL_NAME = "llama-3.1-8b-instant"

# Initialize Flask app
app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Create the chat completion
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )

        # ✅ Access the message content using dot notation (correct way)
        answer = response.choices[0].message.content

        return jsonify({"response": answer}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
