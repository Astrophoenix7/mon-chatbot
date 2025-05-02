from flask import Flask, render_template, request, jsonify
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # <-- charge le .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

# Clé API à configurer plus tard
# openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    
    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    try:
        #response = openai.ChatCompletion.create(
        response = client.chat.completions.create(    
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        #reply = response.choices[0].message["content"].strip()
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)