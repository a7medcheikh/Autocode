from flask import Flask, request
import pandas as pd
import os
import requests

app = Flask(__name__)

# Configuration Telegram (utilisez des variables d'environnement !)
TELEGRAM_TOKEN = os.getenv("7348329316:AAEoJtYgzaIj1jrGVsfjhKpDroT6rnUreMM")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Chargement du fichier Excel
df = pd.read_excel("error_codes.xlsx")

def search_error_code(code):
    result = df[df["الكود"] == code]
    return result.iloc[0] if not result.empty else None

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"].strip().upper()
        
        error_info = search_error_code(text)
        if error_info:
            response = f"""
*الكود*: {error_info['الكود']}
*الوصف*: {error_info['الوصف بالعربية']}
"""
        else:
            response = "⚠️ الكود غير موجود"
        
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": response, "parse_mode": "Markdown"}
        )
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
