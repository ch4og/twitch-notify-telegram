import telebot
import time
import os
import threading
import json
import requests

from dotenv import load_dotenv
load_dotenv()

session = requests.Session()
bot = telebot.TeleBot(os.getenv('TG_API'))
session.timeout = 60
online = False
bot.session = session

button_subscribe = telebot.types.KeyboardButton('Подписаться на уведомления')
button_unsubscribe = telebot.types.KeyboardButton('Отписаться от уведомлений')
button_info = telebot.types.KeyboardButton('Информация о подписке')

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keyboard.add(button_subscribe, button_unsubscribe)
keyboard.add(button_info)

streamer = os.getenv("STREAMER")
link = f"https://www.twitch.com/{streamer}"
tw_client = os.getenv('TW_CLIENT')
tw_token = 'Bearer ' + os.getenv('TW_TOKEN')


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
                 'Привет! Это бот для уведомлений ' +
                 f'о стримах на канале [{streamer}]({link}).',
                 parse_mode='Markdown',
                 reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if (message.text == "Подписаться на уведомления"):
        if add_to_subs(message.chat.id):
            bot.reply_to(message,
                         'Вы успешно подписались.',
                         reply_markup=keyboard)
        else:
            bot.reply_to(message,
                         'Вы уже подписаны.',
                         reply_markup=keyboard)
    elif (message.text == "Отписаться от уведомлений"):
        if rem_from_subs(message.chat.id):
            bot.reply_to(message,
                         'Вы успешно отписались.',
                         reply_markup=keyboard)
        else:
            bot.reply_to(message,
                         'Вы не были подписаны.',
                         reply_markup=keyboard)
    elif (message.text == "Информация о подписке"):
        if str(message.chat.id) in read_subs():
            bot.reply_to(message,
                         "Поскольку вы подписаны на уведомления," +
                         " вы будете получать сообщения когда " +
                         f"[{streamer}]({link}) запускает стрим.",
                         parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.reply_to(message,
                         "Если вы хотите получать уведомления о " +
                         f"cтримах [{streamer}]({link}), подпишитесь " +
                         "на них. В противном случае, " +
                         "вы не будете получать сообщения о запуске стрима",
                         parse_mode='Markdown', reply_markup=keyboard)
    else:
        bot.reply_to(message,
                     "Извините, я вас не понял, " +
                     "используйте кнопки.", reply_markup=keyboard)
        log(f"?{message.chat.username or message.chat.id} - {message.text}")


def check_stream_status():
    global subscribers
    global online
    headers = {
        'Client-ID': tw_client,
        'Authorization': tw_token,
    }

    url = f'https://api.twitch.tv/helix/streams?user_login={streamer}'
    try:
        stream = requests.get(url,
                              headers=headers,
                              timeout=60).json()['data'][0]['title']
        if online is not True:
            for chat_id in read_subs():
                bot.send_message(chat_id,
                                 f'{streamer} запустил стрим!' +
                                 f'\n{stream}\n\n{link}\n{link}')
                log(f"sent {bot.get_chat(chat_id).username or chat_id}")
                online = True
    except IndexError:
        online = False
    except Exception as e:
        log(f"err {e}")
        online = False


def read_subs():
    with open("subscribers.json", "r") as f:
        return json.load(f)


def add_to_subs(chat_id):
    chat_id = str(chat_id)
    subscribers = read_subs()
    if chat_id not in subscribers:
        subscribers[chat_id] = True
        with open("subscribers.json", "w") as f:
            json.dump(subscribers, f)
        return (True)
    else:
        return (False)


def rem_from_subs(chat_id):
    chat_id = str(chat_id)
    subscribers = read_subs()
    if chat_id in subscribers:
        del subscribers[chat_id]
        with open("subscribers.json", "w") as f:
            json.dump(subscribers, f)
            return True
    else:
        return False


def log(inp):
    with open('msg.log', 'a') as f:
        f.write(inp+"\n")


def run_check_stream_status():
    while True:
        check_stream_status()
        if online:
            time.sleep(1800)
        else:
            time.sleep(60)


if __name__ == '__main__':
    # Start a new thread for the check_stream_status() function
    t = threading.Thread(target=run_check_stream_status)
    t.start()
    # Start the bot's polling mechanism in the main thread
    bot.polling(none_stop=True)
