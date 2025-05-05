import os
import telebot
from dotenv import load_dotenv
import psycopg2

load_dotenv()
BOT_TOKEN = os.getenv("BOT_API_TOKEN")

if not BOT_TOKEN:
    print("❌ No BOT_API_TOKEN found! Check .env or GitHub Secrets.")

# Define parameters
bot = telebot.TeleBot(BOT_TOKEN)
uname = ''
uid = 'EMPTY_UID'

# Set bot commands
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Приветствие"),
    telebot.types.BotCommand("/help", "Команды"),
    telebot.types.BotCommand("/play", "Играть"),
    telebot.types.BotCommand("/top", "Лидерборд"),
    telebot.types.BotCommand("/me", "Ваш рейтинг"),
    telebot.types.BotCommand("/setname", "Поменять ник"),
    telebot.types.BotCommand("/debug", "Не забудь удалить ;)"),
])


# Helper function to get a database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            os.environ["DATABASE_URL"],
            sslmode="verify-full",
            sslrootcert=os.getenv("SSL_CERT"),
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None


@bot.message_handler(commands=['start'])
def start(message):
    global uname, uid

    # Collecting user data
    user = message.from_user
    uname = user.first_name or "NO_USERNAME"
    uid = user.id

    # Creating a connection to the database
    conn = get_db_connection()
    if conn is None:
        bot.send_message(message.chat.id, "⚠️ Ошибка подключения к базе данных.")
        return

    try:
        with conn.cursor() as db:
            # Checking if the user exists
            db.execute("SELECT * FROM users WHERE uid = %s", (uid,))
            existing_user = db.fetchone()
            if not existing_user:
                # If needed, adding the user to the database
                db.execute(
                    "INSERT INTO users (uid, uname, score) VALUES (%s, %s, %s)",
                    (uid, uname, 0)
                )
                conn.commit()

                # Informing user if not in headless mode
                bot.send_message(message.chat.id, "👋 Приветсвую! вы зарегистрированы для игры. \n Переходите по ссылке из /play и играйте.")
            else:
                bot.send_message(message.chat.id, "👋 С возвращением! \n Переходите по ссылке из /play и играйте.")
    except psycopg2.Error as e:
        bot.send_message(message.chat.id, "⚠️ Ошибка базы данных. Попробуйте позже.")
        print(f"Database error: {e}")
    finally:
        conn.close()

# Showing all commands and their usage to user
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


@bot.message_handler(commands=['play'])
def play(message):
    global uid
    # If no uid found running start in headless mode to fetch user data
    if uid == 'EMPTY_UID':
        start(message, True)
    # Sending user personal url with query of user uid
    bot.send_message(message.chat.id, f"Вот ваша ссылка на игру \n https://radiohack-website.vercel.app/game?uid=" + str(uid))


@bot.message_handler(commands=['top'])
def top(message):

    # Creating a connection to the database
    conn = get_db_connection()
    if conn is None:
        bot.send_message(message.chat.id, "⚠️ Ошибка подключения к базе данных.")
        return

    try:
        # Fetching top 5 scorers
        with conn.cursor() as db:
            db.execute("""
                       SELECT uname, score FROM users
                       ORDER BY score DESC LIMIT 5;
                       """)
            leaders = db.fetchall()

            message = '''
🏆 Лидеры 🏆  
'''
            # Constructing leaders list message
            for idx, (username, score) in enumerate(leaders):
                if idx == 0:
                    emoji = '🥇'
                elif idx == 1:
                    emoji = '🥈'
                elif idx == 2:
                    emoji = '🥉'
                else:
                    emoji = '⭐'
                message += f"\n{emoji} {username}: {score} pts"

            bot.send_message(message.chat.id, message)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при получении рейтинга")
        print(f'Error getting leaders: {e}')
    finally:
        conn.close()


@bot.message_handler(commands=['me'])
def me(message):
    global uname, uid

    # If uid or uname not found running start in headless mode to fetch user data
    if uid == 'EMPTY_UID' or uname == '':
        start(message, True)

    # Creating a connection to the database
    conn = get_db_connection()
    if conn is None:
        bot.send_message(message.chat.id, "⚠️ Ошибка подключения к базе данных.")
        return

    try:
        # fetching all users and finding the needed one 
        with conn.cursor() as cursor:
            cursor.execute('''
                           WITH RankedUsers AS (SELECT *, RANK() OVER (ORDER BY score DESC) AS rank FROM users)
                           SELECT rank, username, score FROM RankedUsers WHERE uid = %s;
                           ''', (uid,))
            result = cursor.fetchone()

        if result:
            position, username, score = result
            response = f"Твое место в рейтинге: {position}\nИмя: {username}\nОчки: {score}"
        else:
            response = "️️⚠️Пользователь не найден."

        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка подключения к базе данных.")
        print(f'Ошибка в поиске пользователя: {e}')
    finally:
        conn.close()


@bot.message_handler(commands=['setname'])
def get_name(message):
    bot.send_message(message.chat.id, 'Введите ваш новый ник')
    bot.register_next_step_handler(message, set_name)


def set_name(message):
    global uname
    new_username = message.text
    if not new_username.isalpha():
        bot.send_message(message.chat.id, '❌ Ник можеть быть только текстом)')
        return
    else:
        bot.send_message(message.chat.id, '✅ Ник обновлён')
        conn = get_db_connection()
        if conn is None:
            bot.send_message(message.chat.id, "⚠️ Ошибка подключения к базе данных.")
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET username=%s WHERE uid=%s;", (new_username, uid))
                conn.commit()
            uname = new_username
        except Exception as e:
            bot.send_message(message.chat.id, f'Ошибка обновления имени: {e}')
        finally:
            conn.close()


bot.infinity_polling()
