import os
import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import psycopg2

load_dotenv()
BOT_TOKEN = os.getenv("BOT_API_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ No BOT_API_TOKEN found! Check .env or GitHub Secrets.")
#Connect to CockroachDB using connection string and ssl certificate
try:
    conn = psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="verify-full",
        sslrootcert=os.getenv("SSL_CERT"),
    )
    cursor = conn.cursor()
except Exception as e:
    print(f"Failed to connect: {e}")

#Define parameters
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

    # Collecting user data
    user = message.from_user
    uname = user.first_name or "NO_USERNAME"
    uid = user.id

    # Creating unique connection to database
    conn = psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="verify-full",
        sslrootcert=os.getenv("SSL_CERT"),
    )

    try:
        with conn.cursor() as db:
            # Checking if user exists
            existing_user = db.execute(
                "SELECT * FROM users WHERE uid = %s",(uid,))
            existing_user = db.fetchone()
            if not existing_user:
                # If needed adding user to database
                db.execute(
                    "INSERT INTO users (uid, uname, score) VALUES (%s, %s, %s)",
                    (uid, uname, 0)
                )

                conn.commit()

                # Informing ser if not in headless mode
                if not headless:
                    bot.send_message(message.chat.id, "✅ Вы зарегистрированы для игры, напишите /play и играйте по ссылке")
            elif not headless:
                bot.send_message(message.chat.id, "👋 С возвращением! \n Переходите по ссылке из /play и играйте.")

    except psycopg2.Error as e:
        conn.rollback()
        bot.send_message(message.chat.id, "⚠️ Ошибка базы данных. Попробуйте позже.")
        print(f"Database error: {e}")
    finally:
        conn.close()

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
    try:
        # Получаем топ пользователей по количеству очков
        cursor.execute("""
            SELECT username, score 
            FROM users 
            ORDER BY score DESC LIMIT 5;
        """)
        leaders = cursor.fetchall()
        
        message_top = '''
🏆 Лидеры 🏆  
'''
        for idx, (username, score) in enumerate(leaders):
            if idx == 0:
                emoji = '🥇'
            elif idx == 1:
                emoji = '🥈'
            elif idx == 2:
                emoji = '🥉'
            else:
                emoji = '⭐'
                5
            message_top += f"\n{emoji} {username}: {score} pts"
        
        bot.send_message(message.chat.id, message_top)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении рейтинга: {e}")



@bot.message_handler(commands=['me'])
def me(message):
    global uname, uid
    try:
        # Определяем позицию текущего игрока среди остальных участников
        cursor.execute('''
            WITH RankedUsers AS (
                SELECT *, RANK() OVER (ORDER BY score DESC) AS rank
                FROM users
            )
            SELECT rank, username, score 
            FROM RankedUsers 
            WHERE id=%s;
        ''', (uid,))
        result = cursor.fetchone()
        
        if result:
            position, username, score = result
            response = f"Твое место в рейтинге: {position}\nИмя: {username}\nОчки: {score}"
        else:
            response = "Пользователь не найден."
        
        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при определении позиции: {e}")

@bot.message_handler(commands=['/setname'])
def get_name(message):
    bot.send_message(message.chat.id, 'Введите ваш новый ник')
    bot.register_next_step_handler(message, set_name)

def set_name(message):
    global uname
    new_username = message.text
    if not new_username.isalpha():
        bot.send_message(message.chat.id, '❌ К сожалению ник можеть быть только текстом)')
        return
    else:
        bot.send_message(message.chat.id, '✅ Ник обновлён')
        try:
            # Обновляем имя пользователя в базе данных
            cursor.execute("UPDATE users SET username=%s WHERE id=%s;", (new_username, uid))
            connection.commit()
            uname = new_username
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка обновления имени: {e}')


bot.infinity_polling()
