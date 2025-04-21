import os
from flask import Flask, request, jsonify
import pandas as pd
import requests
import logging

# Configuration initiale
app = Flask(__name__)

# Configurer les logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables d'environnement (à définir sur Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
EXCEL_FILE = "error_codes.xlsx"  # Assurez-vous qu'il est présent dans le dépôt GitHub

# Vérification des fichiers et dépendances au démarrage
logger.info("=== Démarrage du bot ===")
logger.info(f"Fichiers présents : {os.listdir('.')}")

try:
    df = pd.read_excel(EXCEL_FILE)
    logger.info("Fichier Excel chargé avec succès")
except Exception as e:
    logger.error(f"ERREUR : Impossible de charger le fichier Excel : {e}")
    raise

# Fonction pour rechercher un code d'erreur
def search_error_code(code):
    try:
        result = df[df["الكود"] == code]
        return result.iloc[0] if not result.empty else None
    except Exception as e:
        logger.error(f"ERREUR lors de la recherche du code : {e}")
        return None

# Route pour le webhook Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        logger.info(f"Reçu : {update}")  # Debug des données entrantes

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"].strip().upper()

            # Recherche du code d'erreur
            error_info = search_error_code(text)

            if error_info:
                response = (
                    f"*الكود*: {error_info['الكود']}\n"
                    f"*الوصف*: {error_info['الوصف بالعربية']}\n"
                    f"*الحل*: {error_info['السبب المحتمل']}"
                )
            else:
                response = "⚠️ الكود غير موجود في قاعدة البيانات"

            # Envoi de la réponse
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": response,
                    "parse_mode": "Markdown"
                }
            )

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"ERREUR dans le webhook : {e}")
        return jsonify({"status": "error"}), 500

# Configuration du webhook (à exécuter une seule fois)
def set_webhook():
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            json={"url": f"https://votre-service.onrender.com/webhook"}
        )
        logger.info("Webhook configuré avec succès")
    except Exception as e:
        logger.error(f"ERREUR lors de la configuration du webhook : {e}")

if __name__ == "__main__":
    # Décommenter la ligne suivante pour configurer le webhook au premier démarrage
     set_webhook()
    app.run(host="0.0.0.0", port=PORT)
