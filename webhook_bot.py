import os
import sys
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в .env")

app = Flask(__name__)
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

is_running = False

def send_message(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
    except Exception as e:
        print(f"Ошибка отправки: {e}")

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    # ... (ваш код обработки команд) ...
    return jsonify({'ok': True})

def run_trading_analysis():
    # ... (ваш код анализа) ...
    return "✅ Готово!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))