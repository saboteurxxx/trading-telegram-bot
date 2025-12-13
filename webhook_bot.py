# webhook_bot.py — финальная версия для Render.com
import os
import sys
import traceback
from flask import Flask, request, jsonify
import requests

# Добавляем путь текущей директории для импорта ваших модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Читаем токен НАПРЯМУЮ из переменных окружения (без dotenv!)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN не задан в Environment Variables на Render")

# Конфигурация Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
is_running = False  # Флаг выполнения анализа

# Инициализация Flask
app = Flask(__name__)

def send_message(chat_id: int, text: str):
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
    """Запуск вашего торгового бота"""
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

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Обработка входящих сообщений от Telegram"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"ok": True})

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if text == "/start":
            send_message(chat_id, "🚀 Бот запущен! Используйте /run для анализа, /status — статус, /price — цена BTC.")

        elif text == "/run":
            send_message(chat_id, "🔄 Запускаю торговый анализ (30–60 сек)...")
            result = run_trading_analysis()
            if len(result) > 4000:
                result = result[:4000] + "\n... (результат сокращён)"
            send_message(chat_id, f"📊 Результат:\n{result}")

        elif text == "/status":
            status = "⏳ Анализ в процессе..." if is_running else "✅ Готов к работе"
            send_message(chat_id, status)

        elif text == "/price":
            try:
                from utils.data_manager import DataManager
                price = DataManager().get_current_price("BTC/USDT")
                if price:
                    send_message(chat_id, f"💰 BTC/USDT: ${price:.2f}")
                else:
                    send_message(chat_id, "❌ Не удалось получить цену")
            except Exception as e:
                send_message(chat_id, f"❌ Ошибка: {str(e)}")

        else:
            send_message(chat_id, "❓ Неизвестная команда. Используйте /start.")

        return jsonify({"ok": True})

    except Exception as e:
        print(f"🔥 Ошибка webhook: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    """Эндпоинт для проверки работоспособности (Render использует его)"""
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)