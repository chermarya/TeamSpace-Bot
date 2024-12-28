import psycopg2
import telebot

bot = telebot.TeleBot("7367187413:AAHYU7auFGrZn7XWIL3pZABfG4YgE8TeXyA")

user_state = {}
user_id = {}


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Hello! Welcome to TeamSpace Support Bot!")
    send_email(message, message.from_user.id)


@bot.message_handler(commands=['report'])
def report_handler(message):
    send_email(message, message.from_user.id)


def send_email(message, user_id):
    user_state[user_id] = {'state': 'WAITING_FOR_EMAIL'}
    bot.send_message(message.chat.id, "Please, enter your email address")


@bot.message_handler(func=lambda message: user_state[message.from_user.id]['state'] == 'WAITING_FOR_EMAIL')
def handle_email_input(message):
    user_state.pop(message.from_user.id)
    user_email = message.text
    user = find_user_in_db(message, user_email)

    if not user == None:
        bot.send_message(message.chat.id, f"""
        <b>Find user:</b>
▫ Username:\t{user[1]}
▫ Full name:\t{user[2]}
▫ Email:\t{user[3]}
▫ Address:\t{user[4]}""", parse_mode='HTML')

        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton('✅ Yes', callback_data='correct_user')
        btn2 = telebot.types.InlineKeyboardButton('❌ No', callback_data='wrong_user')
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, "Is this data correct?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Cannot find user with email \"{user_email}\"")
        send_email(message, message.from_user.id)


@bot.message_handler(func=lambda message: user_state[message.from_user.id]['state'] == 'WAITING_FOR_MESSAGE')
def handle_email_input(message):
    text = message.text
    id = user_id[message.from_user.id]['id']
    try:
        connection = psycopg2.connect(
            dbname='d5t7e9lfmff5dr',
            user='u851cr50ug5urc',
            password='p322a81b96e38ad10bc7b3a8682014b13c7c370ddc89a4a4b89d9b64944ad099a',
            host='clhtb6lu92mj2.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com',
            port='5432'
        )
        cursor = connection.cursor()
        query = f"INSERT INTO reports (user_id, message_text) VALUES ({id}, '{text}')"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        return 0

    bot.send_message(message.chat.id, f"Your report has been sent successfully")
    bot.send_message(message.chat.id, f"For sending a report use the command:\n/report")


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(call):
    if call.data == "correct_user":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, "Enter a message describing your issue")
        user_state[call.from_user.id] = {'state': 'WAITING_FOR_MESSAGE'}
    elif call.data == "wrong_user":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        send_email(call.message, call.from_user.id)


def find_user_in_db(message, email):
    try:
        connection = psycopg2.connect(
            dbname='d5t7e9lfmff5dr',
            user='u851cr50ug5urc',
            password='p322a81b96e38ad10bc7b3a8682014b13c7c370ddc89a4a4b89d9b64944ad099a',
            host='clhtb6lu92mj2.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com',
            port='5432'
        )
        cursor = connection.cursor()
        query = f"SELECT user_id, username, full_name, email, address FROM users WHERE email = '{email}'"
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user is not None:
            user_id[message.from_user.id] = {'id': user[0]}
            res = []
            for i in user:
                res.append(i)
            return res
    except Exception as e:
        return {}


if __name__ == "__main__":
    bot.polling(none_stop=True)
