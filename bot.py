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
    bot.send_message(message.chat.id, r"""
    📚 **Команды Бота** 📚 
    
    ℹ️ /help Показывает этот список команд 
    🎮 /play Даёт вам ссылку на игру
    🏆 /top Посмотрите на лидеров по рейтингу
    😎 /me Посмотрите на каком месте вы в рейтинге 
    🛠️ /debug Не забудь удалить ;\)""",
    parse_mode="MarkdownV2")


@bot.message_handler(commands=['debug'])
def debug(message):
    user = message.from_user

    bot.send_message(message.chat.id, f"""
        🆔 User ID: {user.id}              
        👤 First Name: {user.first_name}    
        📛 Last Name: {user.last_name}      
        🌐 Username: @{user.username}       
        📱 Language: {user.language_code}  
        🤖 Is Bot: {user.is_bot}            
        """)

@bot.message_handler(commands=['play'])
def play(message):
    bot.send_message(message.chat.id, 'this feature is WIP')

@bot.message_handler(commands=['top'])
def top(message):
    bot.send_message(message.chat.id, 'this feature is WIP')

@bot.message_handler(commands=['me'])
def me(message):
    bot.send_message(message.chat.id, 'this feature is WIP')

bot.infinity_polling()