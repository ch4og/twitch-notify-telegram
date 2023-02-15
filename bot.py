import telegram
import os
import requests
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater

load_dotenv()


# Set up Twitch API client and get streamer ID
headers = {
    'Client-ID': os.getenv('TW_CLIENT'),
    'Authorization': f'Bearer {os.getenv("TW_OAUTH")}'
}
params = {
    'login': os.getenv('idobibot')
}
response = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=params).json()
streamer_id = response['data'][0]['id']

# Set up Telegram bot
bot = telegram.Bot(token=os.getenv('TG_API'))
updater = Updater(token=os.getenv('TG_API'), use_context=True)

# Dictionary to store subscribed chat IDs
subscribers = {}

# Handler for /start command
def start(update, context):
    # Add the user's chat ID to the subscribers dictionary
    chat_id = update.message.chat_id
    subscribers[chat_id] = True
    update.message.reply_text('Вы подписались на уведомления. Используйте /stop для отписки.')

# Handler for /stop command
def stop(update, context):
    # Remove the user's chat ID from the subscribers dictionary
    chat_id = update.message.chat_id
    if chat_id in subscribers:
        del subscribers[chat_id]
    update.message.reply_text('Вы отписались от уведомлений. Используйте /start для подписки.')

# Check stream status every minute and send notification if it goes live
def check_stream_status(context):
    response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params={'user_id': streamer_id}).json()
    if response['data']:
        for chat_id in subscribers:
            bot.send_message(chat_id=chat_id, text='{} запустил стрим!'.format('STREAMER_USERNAME'))

# Set up the dispatcher and add the handlers
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('stop', stop))

# Set up the job queue to check stream status every minute
job_queue = updater.job_queue
job_queue.run_repeating(check_stream_status, interval=60, first=0)

# Start the bot
updater.start_polling()
updater.idle()