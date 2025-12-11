# webhook_bot.py — для Render.com
import os
import sys
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

# Добавляем текущую папку в путь импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Загрузка токена из .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в .env")

# Настройки
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
is_running = False

# Инициализация Flask
app = Flask(__name__)

def send_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    try:
        requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print(f"⚠️ Ошибка отправки: {e}")

def run_trading_analysis():
    """Запуск торгового анализа"""
    global is_running
    is_running = True
    try:
        from main_simple import main as trading_bot_main
        result = trading_bot_main()
        return f"✅ Анализ завершён:\n{str(result)}" if result else "✅ Готово!"
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg
    finally:
        is_running = False

@app.route("/webhook", methods=['POST'])
def telegram_webhook():
    """Обработка входящих сообщений от Telegram"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'ok': True})

        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()

        if text == "/start":
            send_message(chat_id, "🚀 Бот работает! Команды: /run, /status, /price")

        elif text == "/run":
            send_message(chat_id, "🔄 Запускаю анализ (30-60 сек)...")
            result = run_trading_analysis()
            if len(result) > 4000:
                result = result[:4000] + "\n... (сокращено)"
            send_message(chat_id, f"📊 Результат:\n{result}")

        elif text == "/status":
            status = "⏳ В процессе..." if is_running else "✅ Готов"
            send_message(chat_id, status)

        elif text == "/price":
            try:
                from utils.data_manager import DataManager
                price = DataManager().get_current_price("BTC/USDT")
                send_message(chat_id, f"💰 BTC/USDT: ${price:.2f}" if price else "❌ Цена не получена")
            except Exception as e:
                send_message(chat_id, f"❌ Ошибка: {e}")

        else:
            send_message(chat_id, "❓ Используйте: /start, /run, /status, /price")

        return jsonify({'ok': True})

    except Exception as e:
        print(f"🔥 Ошибка webhook: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route("/health")
def health_check():
    """Проверка работоспособности"""
    return "OK", 200

if __name__ == "__main__":
    # Render передаёт PORT через окружение
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)