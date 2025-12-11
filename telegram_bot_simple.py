import os
import sys
import time
import json
import traceback
import requests
from dotenv import load_dotenv

# ============================================
# ДИРЕКТОРИЯ И ЛОГИРОВАНИЕ
# ============================================

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ============================================
# ЗАГРУЗКА .ENV
# ============================================

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: TELEGRAM_BOT_TOKEN не найден в .env")
    print("Добавьте: TELEGRAM_BOT_TOKEN=ваш_токен")
    exit(1)

# ============================================
# КЛАСС БОТА
# ============================================

class SimpleTelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.is_running = False  # Флаг выполнения анализа

    def send_message(self, chat_id, text):
        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return {"ok": False}

    def get_updates(self):
        try:
            response = requests.get(
                f"{self.base_url}/getUpdates",
                params={"offset": self.last_update_id + 1, "timeout": 10},
                timeout=15
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("result", []) if result.get("ok") else []
            return []
        except Exception as e:
            print(f"❌ Ошибка получения обновлений: {e}")
            return []

    def run_trading_analysis(self):
        """Запуск торгового бота с флагом выполнения"""
        self.is_running = True
        try:
            from main_simple import main as trading_bot_main
            result = trading_bot_main()
            return f"✅ Анализ завершен:\n{str(result)}" if result else "✅ Торговый анализ выполнен успешно!"
        except Exception as e:
            error_msg = f"❌ Ошибка в торговом боте:\n{str(e)}"
            print(error_msg)
            traceback.print_exc()
            return error_msg
        finally:
            self.is_running = False

    def get_current_price(self):
        try:
            from utils.data_manager import DataManager
            dm = DataManager()
            price = dm.get_current_price("BTC/USDT")
            return price
        except Exception as e:
            print(f"❌ Ошибка получения цены: {e}")
            return None

    def process_message(self, chat_id, text):
        print(f"📨 Команда от {chat_id}: {text}")

        if text == "/start":
            msg = (
                "🚀 <b>Торговый бот для Binance</b>\n\n"
                "Доступные команды:\n"
                "• <code>/start</code> — это сообщение\n"
                "• <code>/run</code> — запустить анализ\n"
                "• <code>/status</code> — проверить статус\n"
                "• <code>/price</code> — текущая цена BTC\n"
                "• <code>/help</code> — справка\n\n"
                "⚠️ <i>Только для обучения!</i>"
            )
            return self.send_message(chat_id, msg)

        elif text == "/run":
            self.send_message(
                chat_id,
                "🔄 <b>Запускаю торговый анализ...</b>\n"
                "⏳ Это займет 1-2 минуты.\n"
                "💡 Вы можете отправить <code>/status</code> для проверки статуса."
            )
            result = self.run_trading_analysis()
            if len(result) > 4000:
                result = result[:4000] + "\n... (результат сокращён)"
            return self.send_message(chat_id, f"📊 <b>Результат анализа:</b>\n{result}")

        elif text == "/status":
            status = "⏳ Анализ в процессе..." if self.is_running else "✅ Готов к работе"
            return self.send_message(chat_id, status)

        elif text == "/price":
            price = self.get_current_price()
            if price:
                return self.send_message(chat_id, f"💰 <b>BTC/USDT:</b> ${price:.2f}")
            else:
                return self.send_message(chat_id, "❌ Не удалось получить цену")

        elif text == "/help":
            msg = (
                "🤖 <b>Торговый бот для Binance</b>\n\n"
                "<b>Функции:</b>\n"
                "• Загрузка данных с Binance\n"
                "• Расчёт индикаторов (MACD, RSI, Bollinger Bands)\n"
                "• ML модель для сигналов BUY/SELL/HOLD\n\n"
                "<b>Технологии:</b>\n"
                "• Python 3.13\n"
                "• pandas, ccxt, ta, scikit-learn\n\n"
                "⚠️ <i>Не используйте для реальной торговли!</i>"
            )
            return self.send_message(chat_id, msg)

        else:
            return self.send_message(chat_id, "❌ Неизвестная команда. Используйте /start.")

    def start_polling(self):
        print("="*60)
        print("🤖 ЗАПУСК ПРОСТОГО TELEGRAM БОТА")
        print("="*60)
        print("📱 Отправьте /start в Telegram")
        print("⏳ Проверка каждые 5 секунд...")
        print("="*60)

        try:
            while True:
                updates = self.get_updates()
                for update in updates:
                    self.last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg["text"].strip()
                        self.process_message(chat_id, text)
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            traceback.print_exc()

# ============================================
# ЗАПУСК
# ============================================

def main():
    bot = SimpleTelegramBot(TELEGRAM_BOT_TOKEN)
    bot.start_polling()

if __name__ == "__main__":
    main()