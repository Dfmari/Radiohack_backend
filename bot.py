import os
import telebot
from dotenv import load_dotenv

load_dotenv()

# Get token from environment (works in GitHub Actions too)
BOT_TOKEN = os.getenv("BOT_API_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ No BOT_API_TOKEN found! Check .env or GitHub Secrets.")

bot = telebot.TeleBot(BOT_TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Приветствие"),
    telebot.types.BotCommand("/help", "Команды"),
    telebot.types.BotCommand("/play", "Играть"),
    telebot.types.BotCommand("/top", "Лидерборд"),
    telebot.types.BotCommand("/me", "Ваш рейтинг"),
    telebot.types.BotCommand("/debug", "Не забудь удалить ;)"),
])

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🔍 Привет детектив 🔍 \n.... Надо сделать приветствие")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "📚 **Команды Бота** 📚 \n \n ℹ️ /help Показывает этот список команд \n \n 🎮 /play Даёт вам ссылку на игру \n \n 🏆 /top Посмотрите на лидеров по рейтингу \n \n 😎 /me Посмотрите на каком месте вы в рейтинге \n \n 🛠️ /debug Не забудь удалить ;)", parse_mode="MarkdownV2")
bot.infinity_polling()

@bot.message_handler(commands=['debug'])
def handle_message(message):
    user = message.from_user

    print(f"""
        🆔 User ID: {user.id}               # Unique Telegram ID (critical for replies)
        👤 First Name: {user.first_name}    # Always present
        📛 Last Name: {user.last_name}      # Optional
        🌐 Username: @{user.username}       # Without the '@' symbol (may be None)
        📱 Language: {user.language_code}   # Like 'en', 'ru', etc. (if set in Telegram settings)
        🤖 Is Bot: {user.is_bot}            # True/False (useful to detect fake users)
        """)