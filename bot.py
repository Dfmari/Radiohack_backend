import os
import telebot
import base64
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_API_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ No BOT_API_TOKEN found! Check .env or GitHub Secrets.")

bot = telebot.TeleBot(BOT_TOKEN)
uname = ''
uid = ''

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Приветствие"),
    telebot.types.BotCommand("/help", "Команды"),
    telebot.types.BotCommand("/play", "Играть"),
    telebot.types.BotCommand("/top", "Лидерборд"),
    telebot.types.BotCommand("/me", "Ваш рейтинг"),
    telebot.types.BotCommand("/setname", "Поменять ник"),
    telebot.types.BotCommand("/debug", "Не забудь удалить ;)"),
])

@bot.message_handler(commands=['start'])
def start(message):
    global uname
    global uid
    bot.send_message(message.chat.id, "🔍 Привет детектив 🔍 \n.... Надо сделать приветствие \n /play кстати ссылку выдаёт)")
    user = message.from_user
    if user.first_name == None:
        uname = "NO_USERNAME"
    else:
        uname = user.first_name

    uid = user.id

    '''
    SQL DATABASE ACTION
    
    Отправляем uname как ник и uid как ключ в базу Users
    
    SQL DATABASE ACTION
    '''



@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, r"""
📚 **Команды Бота** 📚 
    
ℹ️ /help Показывает этот список команд 
🎮 /play Даёт вам ссылку на игру
🏆 /top Посмотрите на лидеров по рейтингу
😎 /me Посмотрите на каком месте вы в рейтинге 
✍️ /setname Поменяй свой ник в рейтинге
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
🤖 Is Bot: {user.is_bot}""")

@bot.message_handler(commands=['play'])
def play(message):
    bot.send_message(message.chat.id, 'when finished the link will look something like this https://radiohack-website.vercel.app/game?uid=s0M3_5tR1ng')
    bot.send_message(message.chat.id, f"Вот ваша ссылка на игру \n https://radiohack-website.vercel.app/game")



@bot.message_handler(commands=['top'])
def top(message):
    bot.send_message(message.chat.id, 'this feature is WIP')

@bot.message_handler(commands=['me'])
def me(message):
    bot.send_message(message.chat.id, 'this feature is WIP')

bot.infinity_polling()