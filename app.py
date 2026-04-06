import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)

BOT_NAME = "Nova"
SYSTEM_PROMPT = """You are Nova, a helpful and friendly AI assistant. 
You are smart, concise, and a professional. You help users with questions, 
ideas, coding problems, writing, and anything else they need. 
Keep responses clear and conversational — not too long unless the user asks for detail."""

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html", bot_name=BOT_NAME)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    history = data.get("history", [])  # list of {role, content} dicts

    if not history:
        return jsonify({"error": "No messages provided"}), 400

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history
        )
        reply = response.content[0].text
        return jsonify({"reply": reply})

    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key. Check your ANTHROPIC_API_KEY environment variable."}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit hit. Please wait a moment and try again."}), 429
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: ANTHROPIC_API_KEY is not set.")
        print("   Set it with: export ANTHROPIC_API_KEY=your_key_here\n")
    app.run(debug=True, port=5000)
