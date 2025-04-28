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
uid = 'EMPTY_UID'

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
def start(message, headless=False):
    global uname, uid
    if not headless:
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
🤖 Is Bot: {user.is_bot}
""")

@bot.message_handler(commands=['play'])
def play(message):
    global uid
    if uid == 'EMPTY_UID':
        start(message, True)
    bot.send_message(message.chat.id, f"Вот ваша ссылка на игру \n https://radiohack-website.vercel.app/game?uid=" + str(uid))


@bot.message_handler(commands=['top'])
def top(message):
    bot.send_message(message.chat.id, 'this feature is WIP')
    '''
    SQL DATABASE ACTION
    
    Запрашиваем uname и score для первых 5? по значению score
    
    SQL DATABASE ACTION
    '''
    leader1 = "Placeholder1"
    score1 = 100
    leader2 = "Placeholder2"
    score2 = 99
    leader3 = "Placeholder3"
    score3 = 98
    leader4 = "Placeholder4"
    score4 = 97
    leader5 = "Placeholder5"
    score5 = 96

    top = [[leader1, score1], [leader2, score2], [leader3, score3], [leader4, score4], [leader5, score5]]
    message_top = '''
🏆 Лидеры 🏆  
'''
    for i in range(len(top)):
        if i == 0:
            emoji = '🥇'
        elif i == 1:
            emoji = '🥈'
        elif i == 2:
            emoji = '🥉'
        else :
            emoji = '⭐'

        message_top += f'\n{emoji} {top[i][0]} {top[i][1]}pts'
    bot.send_message(message.chat.id, message_top)



@bot.message_handler(commands=['me'])
def me(message):
    global uname, uid
    '''
    SQL DATABASE ACTION

    Запрашиваем место данного uid в списке относительно score

    SQL DATABASE ACTION
    '''
    bot.send_message(message.chat.id, 'this feature is WIP')

@bot.message_handler(commands=['/setname'])
def get_name(message):
    bot.send_message(message.chat.id, 'Введите ваш новый ник')
    bot.register_next_step_handler(message, set_name)

def set_name(message):
    global uname
    old_uname = uname
    uname = message.text
    if not uname.isalpha():
        bot.send_message(message.chat.id, '❌ К сожалению ник можеть быть только текстом)')
        uname = old_uname
        return
    else:
        bot.send_message(message.chat.id, '✅ Ник обновлён')
'''
            SQL DATABASE ACTION

            Заменяем в Users имя old_uname на uname

            SQL DATABASE ACTION
            '''


bot.infinity_polling()