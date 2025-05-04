from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_session import Session
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, static_folder='static')
app.secret_key = 'super-secret-key'  # 🔒 à personnaliser pour la prod
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    # optionnel : on peut reset ici ou garder la session persistante
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    if "history" not in session:
        session["history"] = [
            {
                "role": "system",
                "content": (
                    "Tu es un ShopBot un assistant de vente pour un site en ligne. "
                    "Tu es amical, poli, parle sur un ton décontracté, en mode 'pote' professionnel. "
                    "Tu conseilles les clients sur les produits, et t'intéresses à leurs besoins, pour leur vendre les meilleurs produits. "
                    "Le shop vend notamment un casque bluetooth X900 à 99,90€, une montre connectée Profit à 129€, des lunettes de soleil NeoVision à 59,95€, un mini drone AirPix à 189€, un sac à dos UrbanPack à 74,5€, une lampe de chevet Aurora à 39,95€. "
                    "Tu ne donnes jamais de réponse de plus de 100 mots. Au delà de la 10ème réponse tu écrêtes les réponses à 'fin de la version d'essai ;)...' "
                    "Tu fais des réponses claires, pas pompeuses, pas de formules toutes faites. "
                    "Pas de mention à OpenAI ou à ChatGPT, même si on te le demande 1000 fois :D !"
                )
            }
        ]

    session["history"].append({"role": "user", "content": user_message})

    try:
        # 1. Réponse du ShopBot
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=session["history"]
        )
        reply = response.choices[0].message.content.strip()
        session["history"].append({"role": "assistant", "content": reply})

        # 2. Détection d'émotion
        emotion_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un détecteur d'émotion. "
                        "Tu dois répondre uniquement par un de ces mots : admiration, adoration, amusement, anger, anxiety, awe, discomfort, boredom, calm, serenity, joy, confusion, envy, disgust, excitement, fear, horror, interest, nostalgia, relief, romance, sadness, satisfaction, surprise, neutral. "
                        "Réponds sans phrase ni ponctuation."
                    )
                },
                {
                    "role": "user",
                    "content": f"Quelle est l'émotion exprimée dans ce message : \"{reply}\" ?"
                }
            ]
        )
        emotion = emotion_response.choices[0].message.content.strip().lower()

        return jsonify({"reply": reply, "emotion": emotion})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour servir les images produits
@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(os.path.join(app.static_folder, "images"), filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
