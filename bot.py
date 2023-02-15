import twitch
import telegram
import os
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater

load_dotenv()

# Set up Twitch API client and get streamer ID
client = twitch.TwitchClient(client_id=os.getenv('TW_CLIENT'), client_secret=os.getenv('TW_OAUTH'))
streamer = client.users.translate_usernames_to_ids(os.getenv('STREAMER'))[0]

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
    update.message.reply_text('Вы подписались на уведомления. Используйте /stop для отмены')

# Handler for /stop command
def stop(update, context):
    # Remove the user's chat ID from the subscribers dictionary
    chat_id = update.message.chat_id
    if chat_id in subscribers:
        del subscribers[chat_id]
    update.message.reply_text('Вы отписались от уведомлений. Используйте /start для отмены.')

# Check stream status every minute and send notification if it goes live
def check_stream_status(context):
    stream = client.streams.get_stream_by_user(streamer.id)
    if stream:
        for chat_id in subscribers:
            bot.send_message(chat_id=chat_id, text='{} запустил стрим!'.format(streamer.display_name))

# Set up the dispatcher and add the handlers
dispatcher = updater.dispatcher
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('stop', stop))

# Set up the job queue to check stream status every minute
job_queue = updater.job_queue
job_queue.run_repeating(check_stream_status, interval=60, first=0)

# Start the bot
updater.start_polling()
updater.idle()