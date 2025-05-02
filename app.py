from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # <-- charge le .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = Flask(__name__)

app.secret_key = 'super-secret-key'  # 🔒 à remplacer par un vrai secret
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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

    # Initialise l'historique si vide
    #if "history" not in session:
    #    session["history"] = []

    if "history" not in session:
        session["history"] = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant amical, qui parle sur un ton décontracté, en mode 'poto'. "
                    "Tu ne donnes jamais de réponse de plus de 100 mots. "
                    "Tu fais des réponses claires, pas pompeuses. "
                    "Pas de formules toutes faites, pas de 'je suis un modèle d'OpenAI'."
                )
            }
        ]


    # Ajoute le message utilisateur à l'historique
    session["history"].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=session["history"]
        )
        reply = response.choices[0].message.content.strip()

        # Ajoute la réponse du bot à l'historique
        session["history"].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)