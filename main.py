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

# Variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
EXCEL_FILE = "error_codes.xlsx"

# Vérification des fichiers
logger.info("=== Démarrage du bot ===")
logger.info(f"Fichiers présents : {os.listdir('.')}")

try:
    df = pd.read_excel(EXCEL_FILE)
    logger.info("Fichier Excel chargé avec succès")
except Exception as e:
    logger.error(f"ERREUR : Impossible de charger le fichier Excel : {e}")
    raise

def search_error_code(code):
    try:
        result = df[df["الكود"] == code]
        return result.iloc[0] if not result.empty else None
    except Exception as e:
        logger.error(f"ERREUR lors de la recherche du code : {e}")
        return None

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        logger.info(f"Reçu : {update}")

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"].strip().upper()

            error_info = search_error_code(text)

            if error_info:
                response = (
                    f"*الكود*: {error_info['الكود']}\n"
                    f"*الوصف*: {error_info['الوصف بالعربية']}\n"
                    f"*الحل*: {error_info['السبب المحتمل']}"
                )
            else:
                response = "⚠️ الكود غير موجود في قاعدة البيانات"

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

def set_webhook():
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            json={"url": f"https://autocode-jg5y.onrender.com/webhook"}
        )
        logger.info("Webhook configuré avec succès")
    except Exception as e:
        logger.error(f"ERREUR lors de la configuration du webhook : {e}")

if __name__ == "__main__":
    # Décommenter pour la première configuration
    # set_webhook()
    app.run(host="0.0.0.0", port=PORT)
