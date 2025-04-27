import os
import requests
import pandas as pd
from flask import Flask, request
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Config Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # plus sécurisé
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Config Google Sheets
SHEET_ID = "142VrKOlnEhRAxbyB0nvjuCaAsptco5R9fjtrTvRSZu0"
SHEET_RANGE = "Sheet1!A:D"

def get_sheet_data():
    try:
        creds = service_account.Credentials.from_service_account_file(
            'service-account.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=SHEET_RANGE).execute()
        values = result.get('values', [])

        if not values:
            return pd.DataFrame()

        return pd.DataFrame(values[1:], columns=values[0])
    except Exception as e:
        print(f"Erreur lecture sheet: {e}")
        return pd.DataFrame()

def search_error_code(code):
    df = get_sheet_data()
    if df.empty:
        return None
    result = df[df["الكود"].str.upper() == code]
    return result.iloc[0] if not result.empty else None

def send_telegram_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.route('/')
def home():
    return "Bot en ligne via Railway!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip().upper()
        result = search_error_code(text)

        if result is not None:
            warning = (
                "تنبيه: هاذا الروبوت تم إنشاؤه بالاستعانة بأدوات الذكاء الصناعي لمساعدتك...\n\n"
            )
            msg = (
                f"{warning}"
                f"*الكود*: {result['الكود']}\n"
                f"*الوصف بالإنجليزية*: {result['الوصف بالإنجليزية']}\n"
                f"*الوصف بالعربية*: {result['الوصف بالعربية']}\n"
                f"*السبب المحتمل*: {result['السبب المحتمل']}\n\n"
                "للتواصل :\n"
                "https://www.youtube.com/@MohamedAhmedCheikh\n"
                "https://www.facebook.com/Mdcheikh02/\n"
                "https://wa.me/message/TTJOOA5V4FQ4L1"
            )
        else:
            msg = "عذرًا، لم يتم العثور على الكود المطلوب..."

        send_telegram_message(chat_id, msg)

    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True)
