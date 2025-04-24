import os
import requests
import pandas as pd
from flask import Flask
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Configuration - Utilisez les variables Railway
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
SHEET_ID = os.environ.get('SHEET_ID', "142VrKOlnEhRAxbyB0nvjuCaAsptco5R9fjtrTvRSZu0")

# Chargez les credentials depuis les variables Railway
def get_google_creds():
    creds_json = os.environ['GOOGLE_CREDS_JSON']  # JSON complet collé dans les variables
    return service_account.Credentials.from_service_account_info(
        creds_json,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"].strip().upper()
        
        error_info = search_error_code(text)
        
        if error_info:
            response = (
                "تنبيه: هاذا الروبوت تم إنشاؤه بالاستعانة بأدوات الذكاء الصناعي\n\n"
                f"*الكود*: {error_info['الكود']}\n"
                f"*الوصف*: {error_info['الوصف بالعربية']}\n"
                f"*الحل*: {error_info['السبب المحتمل']}\n\n"
                "للتواصل:\n"
                "https://youtube.com/@MohamedAhmedCheikh"
            )
        else:
            response = "⚠️ الكود غير موجود"
            
        send_telegram_message(chat_id, response)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
