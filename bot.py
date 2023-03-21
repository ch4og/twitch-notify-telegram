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

# Create the reply markup keyboard
keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

# Add the first two buttons to the keyboard
keyboard.add(button_subscribe, button_unsubscribe)

# Add the third button to the row below
keyboard.add(button_info)

# keyboard = [
#    ['Подписаться на уведомления', 'Отписаться от уведомлений'],
#    ['Информация о подписке']
#  ];

@bot.message_handler(commands = ['start'])
def start(message):
    bot.reply_to(message, f'Привет!\nЭто бот для уведомлений о стримах на канале {os.getenv("STREAMER")}!', reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if (message.text == "Подписаться на уведомления"):
        if add_to_subs(message.chat.id):
            bot.reply_to(message, f'Вы успешно подписались.', reply_markup=keyboard)
            if message.chat.username:
                log(f"{message.chat.username} subscribed")
            else:
                log(f"{message.chat.id} subscribed")
        else:
            bot.reply_to(message, f'Вы уже подписаны.', reply_markup=keyboard)
        
    elif (message.text == "Отписаться от уведомлений"):
        if rem_from_subs(message.chat.id):
            bot.reply_to(message, f'Вы успешно отписались.', reply_markup=keyboard)
            if message.chat.username:
                log(f"{message.chat.username} unsubscribed")
            else:
                log(f"{message.chat.id} unsubscribed")
        else:
            bot.reply_to(message, f'Вы не были подписаны.', reply_markup=keyboard)
  #              messageText = `Поскольку вы подписаны на уведомления, вы будете получать сообщения каждый раз когда [${streamer}](${link}) запускает стрим.`;
  #          } else {
  #            messageText = `Если вы хотите получать уведомления о cтримах [${streamer}](${link}), подпишитесь на них. В противном случае, вы не будете получать сообщения о запуске стрима`;
  #          }
  elif (message.text == "Информация о подписке"):
        sample = f"Подписавшись на уведомления вы будете получать сообщения каждый раз когда [{os.getenv('STREAMER')}]({os.getenv('LINK')}) запускает стрим. \nВ случае ошибок пишите @{os.getenv('DEV')}"
        if str(message.chat.id) in read_subs():
            bot.reply_to(message, f"**Вы подписаны на уведомления.** \n\n{sample}", parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.reply_to(message, f"**Вы не подписаны на уведомления.** \n\n{sample}", parse_mode='Markdown', reply_markup=keyboard)
    elif (message.text == "sysi"):
        if (message.chat.username == os.getenv('DEV')):
            users = []
            with open('msg.log', 'r') as file:
                logg = file.read()
            for chat_id in read_subs():
                if message.chat.username:
                    users.append("@"+bot.get_chat(chat_id).username)   
                else:
                    users.append(f"[@{chat_id}](tg://user?id={chat_id})")
            bot.reply_to(message, f"online={online}\n\nSUBS:\n{' '.join(users)}\n\nLOG:\n{logg}", reply_markup=keyboard)
        else:
            if message.chat.username:
                log(f"!!!{message.chat.username} - {message.text}")
            else:
                log(f"!!!{message.chat.id} - {message.text}")
            bot.reply_to(message, f'Извините, я вас не понял, используйте кнопки.', reply_markup=keyboard)
    else:
        bot.reply_to(message, f'Извините, я вас не понял, используйте кнопки.', reply_markup=keyboard)
        if message.chat.username:
            log(f"?{message.chat.username} - {message.text}")
        else:
            log(f"?{message.chat.id} - {message.text}")
         
def check_stream_status():
    global subscribers
    global online
    headers = {
        'Client-ID': os.getenv('TW_CLIENT'),
        'Authorization': f"Bearer {os.getenv('TW_OAUTH')}",            
    }

    url = f'https://api.twitch.tv/helix/streams?user_login={os.getenv("STREAMER")}'
    try:
        stream = requests.get(url, headers=headers, timeout=60).json()['data'][0]['title']
        if online != True:
            for chat_id in read_subs():
                bot.send_message(chat_id, f'{os.getenv("STREAMER")} запустил стрим!\n{stream}\n\nhttps://www.twitch.tv/{os.getenv("STREAMER")}\nhttps://www.twitch.tv/{os.getenv("STREAMER")}')
                username = bot.get_chat(chat_id).username
                if username:
                    log(f"SENT TO {username}")
                else:
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
