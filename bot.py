import telebot
import time
import os
import threading
import json
import requests

from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TG_API'))

# Dictionary to store subscribed chat IDs

online = False

button_subscribe = telebot.types.KeyboardButton('Подписаться на уведомления')
button_unsubscribe = telebot.types.KeyboardButton('Отписаться от уведомлений')
button_info = telebot.types.KeyboardButton('Информация о подписке')

# Create the reply markup keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

# Add the first two buttons to the keyboard
keyboard.add(button_subscribe, button_unsubscribe)

# Insert the third button below the first two buttons
keyboard.insert(button_info)

@bot.message_handler(commands = ['start'])
def start(message):
    bot.reply_to(message, f'Привет!\nЭто бот для уведомлений о стримах на канале {os.getenv("STREAMER")}!', reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if (message.text == "Подписаться на уведомления"):
        if add_to_subs(message.chat.id):
            bot.reply_to(message, f'Вы успешно подписались.')
            log(f"{message.chat.username} subscribed ({message.chat.id})")
        else:
            bot.reply_to(message, f'Вы уже подписаны.')
        
    elif (message.text == "Отписаться от уведомлений"):
        if rem_from_subs(message.chat.id):
            bot.reply_to(message, f'Вы успешно отписались.')
            log(f"{message.chat.username} unsubscribed ({message.chat.id})")
        else:
            bot.reply_to(message, f'Вы не были подписаны.')
    elif (message.text == "Информация о подписке"):
        if str(message.chat.id) in read_subs():
            bot.reply_to(message, f"Подписавшись на уведомления вы будете получать сообщения каждый раз когда {os.getenv('STREAMER')} запускает стрим. \n\nВы подписаны на уведомления.")
        else:
            bot.reply_to(message, f"Подписавшись на уведомления вы будете получать сообщения каждый раз когда {os.getenv('STREAMER')} запускает стрим. \n\nВы не подписаны на уведомления.")
    elif (message.text == "sysi"):
        if (message.chat.username == "ch4og"):
            with open('msg.log', 'r') as file:
                logg = file.read()
            bot.reply_to(message, f"online={online}\n\nLOG:\n{logg}")
        else:
            log(f"!!!{message.chat.username} - {message.text} ({message.chat.id})")
    else:
         bot.reply_to(message, f'Извините, я вас не понял, используйте кнопки. В случае ошибки воспользуйтесь /start')
         log(f"?{message.chat.username} - {message.text} ({message.chat.id})")
         
def check_stream_status():
    global subscribers
    global online
    headers = {
        'Client-ID': os.getenv('TW_CLIENT'),
        'Authorization': f"Bearer {os.getenv('TW_OAUTH')}",            
    }

    url = f'https://api.twitch.tv/helix/streams?user_login={os.getenv("STREAMER")}'
    try:
        stream = requests.get(url, headers=headers, timeout=5).json()['data'][0]['title']
        if online != True:
            for chat_id in read_subs():
                bot.send_message(chat_id, f'{os.getenv("STREAMER")} запустил стрим!\n{stream}\n\nhttps://www.twitch.tv/{os.getenv("STREAMER")}\nhttps://www.twitch.tv/{os.getenv("STREAMER")}')
                log(f"SENT TO {chat_id}")
                online = True
    except:
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
        return(True)
    else:
        return(False)

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
        time.sleep(60)

if __name__ == '__main__':
    # Start a new thread for the check_stream_status() function
    t = threading.Thread(target=run_check_stream_status)
    t.start()
    
    # Start the bot's polling mechanism in the main thread
    bot.polling(none_stop=True)