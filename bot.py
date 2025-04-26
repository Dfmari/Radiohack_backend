import os
import telebot

# Try to load from .env (for local development)
from dotenv import load_dotenv
load_dotenv()

# Get token from environment (works in GitHub Actions too)
BOT_TOKEN = os.getenv("API_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ No TELEGRAM_BOT_TOKEN found! Check .env or GitHub Secrets.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message, "🔍 Привет детектив 🔍 \n.... Надо сделать приветствие")