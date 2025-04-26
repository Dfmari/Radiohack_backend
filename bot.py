import os
import telebot
from dotenv import load_dotenv

load_dotenv()

# Get token from environment (works in GitHub Actions too)
BOT_TOKEN = os.getenv("BOT_API_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ No TELEGRAM_BOT_TOKEN found! Check .env or GitHub Secrets.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔍 Привет детектив 🔍 \n.... Надо сделать приветствие")

bot.infinity_polling()