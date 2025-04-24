import os
import requests
import pandas as pd
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

app = Flask(__name__)

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Telegram
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Configuration Google Sheets
SHEET_ID = os.environ.get('SHEET_ID', "142VrKOlnEhRAxbyB0nvjuCaAsptco5R9fjtrTvRSZu0")
SHEET_RANGE = "Sheet1!A:D"  # Ajustez selon votre structure

# Initialisation des credentials Google
def get_google_creds():
    try:
        # Version Railway (avec variable d'environnement)
        creds_json = os.environ['GOOGLE_CREDS_JSON']
        return service_account.Credentials.from_service_account_info(
            eval(creds_json),
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
    except Exception as e:
        logger.error(f"Erreur Google Sheets: {e}")
        return None

# Endpoint de santé pour Railway
@app.route('/health')
def health_check():
    return "OK", 200

# Fonction pour lire les données du Google Sheet
def get_sheet_data():
    try:
        creds = get_google_creds()
        if not creds:
            return pd.DataFrame()
            
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=SHEET_RANGE
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return pd.DataFrame()
            
        return pd.DataFrame(values[1:], columns=values[0])
        
    except Exception as e:
        logger.error(f"Erreur Google Sheets: {e}")
        return pd.DataFrame()

# Fonction de recherche des codes d'erreur
def search_error_code(code):
    df = get_sheet_data()
    if df.empty:
        return None
        
    result = df[df["الكود"].str.upper() == code.upper()]
    return result.iloc[0] if not result.empty else None

# Envoi des réponses Telegram
def send_telegram_message(chat_id, text):
    try:
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
        )
    except Exception as e:
        logger.error(f"Erreur d'envoi Telegram: {e}")

# Configuration automatique du webhook
def setup_webhook():
    try:
        webhook_url = f"https://{os.environ['RAILWAY_PUBLIC_DOMAIN']}/webhook"
        response = requests.post(
            f"{TELEGRAM_API_URL}/setWebhook",
            json={"url": webhook_url}
        )
        logger.info(f"Webhook configuré: {response.json()}")
    except Exception as e:
        logger.error(f"Erreur configuration webhook: {e}")

# Endpoint principal
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.json
        if "message" not in update:
            return "OK", 200
            
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "").strip()
        
        if not text:
            return "OK", 200
            
        # Recherche du code d'erreur
        error_info = search_error_code(text)
        
        if error_info:
            response = (
                "⚠️ *تنبيه*: هذه المعلومات استرشادية فقط\n\n"
                f"*الكود*: {error_info['الكود']}\n"
                f"*الوصف*: {error_info['الوصف بالعربية']}\n"
                f"*الحل المقترح*: {error_info['السبب المحتمل']}\n\n"
                "للاستفسار:\n"
                "https://wa.me/message/TTJOOA5V4FQ4L1"
            )
        else:
            response = "⚠️ عذراً، لم يتم العثور على هذا الكود. يرجى التحقق وإعادة المحاولة."
            
        send_telegram_message(chat_id, response)
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        return "ERR", 500

# Point d'entrée
if __name__ == "__main__":
    # Configurer le webhook au premier démarrage
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
        setup_webhook()
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
