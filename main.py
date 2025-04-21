import os
from flask import Flask, request
import pandas as pd
import requests

app = Flask(__name__)

# Configuration
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "error_codes.xlsx")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Debug initial
print("=== Démarrage ===")
print("Fichiers:", os.listdir("."))
print("Token présent:", bool(TELEGRAM_TOKEN))

try:
    df = pd.read_excel(EXCEL_FILE)
    print("Excel chargé avec succès")
except Exception as e:
    print("ERREUR Excel:", e)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = request.get_json()
        print("Reçu:", update)  # Debug
        
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"].strip().upper()
            
            # ... (votre logique existante)
            
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": "Test réponse", "parse_mode": "Markdown"}
            )
        return "OK", 200
    except Exception as e:
        print("ERREUR webhook:", e)
        return "ERR", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
