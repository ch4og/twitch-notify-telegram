const fs = require('fs');
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

require('dotenv').config();

let online = false;
const tw_cli = process.env.TW_CLIENT;
const tw_key = process.env.TW_SECRET;
const streamer = process.env.STREAMER;
const tg_api = process.env.TG_API;
const link = process.env.LINK;


const keyboard = [
    ['Подписаться на уведомления', 'Отписаться от уведомлений'],
    ['Информация о подписке']
  ];

const bot = new TelegramBot(tg_api, { polling: true });

  bot.on('message', (msg) => {
    const messageText = msg.text;
    const chatId = msg.chat.id;
    switch (messageText) {
      case '/start':
        bot.sendMessage(chatId, `Привет!\nЭто бот для уведомлений о стримах на канале ${streamer}!`, {
          reply_markup: { keyboard: keyboard, resize_keyboard: true, },
          reply_to_message_id: msg.message_id,
        });
        break;

      case 'Подписаться на уведомления':
        if (addToSubs(chatId, msg.from.username || "nooagainuserid"+chatId)){//
            uss = getUname(chatId, msg.from.username);
          log(`${uss} subscribed`);
          bot.sendMessage(chatId, `Вы успешно подписались.`, {
            reply_markup: { keyboard: keyboard, resize_keyboard: true, },
            reply_to_message_id: msg.message_id,
          });
        } else {
            bot.sendMessage(chatId, `Вы уже подписаны.`, {
                reply_markup: { keyboard: keyboard, resize_keyboard: true, },
                reply_to_message_id: msg.message_id,
              });
          }
          break;

      case 'Отписаться от уведомлений':
        if (remFromSubs(chatId)){
            
            uss = getUname(chatId, msg.from.username);
            log(`${uss} unsubscribed`);
            bot.sendMessage(chatId, `Вы успешно отписались.`, {
                reply_markup: { keyboard: keyboard, resize_keyboard: true, },
                reply_to_message_id: msg.message_id,
              });
        } else {
            bot.sendMessage(chatId, `Вы не были подписаны.`, {
                reply_markup: { keyboard: keyboard, resize_keyboard: true, },
                reply_to_message_id: msg.message_id,
              });
        }
        break;
          case 'Информация о подписке':
            const subs = readSubs();
            let messageText = '';
            if (Object.keys(subs).includes(chatId.toString())) {
              messageText = `Поскольку вы подписаны на уведомления, вы будете получать сообщения каждый раз когда [${streamer}](${link}) запускает стрим.`;
            } else {
              messageText = `Если вы хотите получать уведомления о cтримах [${streamer}](${link}), подпишитесь на них. В противном случае, вы не будете получать сообщения о запуске стрима`;
            }
            bot.sendMessage(chatId, messageText, {
              reply_markup: { keyboard: keyboard, resize_keyboard: true,},
              reply_to_message_id: msg.message_id,
              parse_mode: 'Markdown'
            }); 
          break;

      default:
        bot.sendMessage(chatId, 'Извините, я вас не понял, используйте кнопки.', {
            reply_markup: { keyboard: keyboard, resize_keyboard: true, },
            reply_to_message_id: msg.message_id
        });
  
        uss = getUname(chatId, msg.from.username);
        log(`?${uss} - ${messageText}`) 
        break;
    }
  });
  bot.on('polling_error', (error) => {
    const { code, message, stack } = error; // Destructuring the error object.
    console.error(`TIME: ${new Date()}\nCODE: ${code}\nMSG: ${message}\nSTACK: ${stack}`);
    process.exit(1);
  });





  const checkStreamStatus = async () => {
    const headers = {
      'Client-ID': tw_cli,
      'Authorization': `Bearer ${tw_key}`,
    };
  
    const url = `https://api.twitch.tv/helix/streams?user_login=${streamer}`;
  
    try {
      if (online === false) {
        let subs = Object.keys(readSubs());
        const response = await axios.get(url, { headers, timeout: 5000 });
        const streamTitle = response.data.data[0].title;
        for (const irs in subs) {
          chatId = subs[irs]
            bot.sendMessage(chatId, `*${streamer} запустил стрим!*\n\n${streamTitle}\n\nhttps://www.twitch.tv/${streamer}\nhttps://www.twitch.tv/${streamer}\nhttps://www.twitch.tv/${streamer}`, {parse_mode: 'Markdown'});
            const username = Object.values(readSubs())[irs]
            console.log(username)
            nameee = getUname(chatId, username);
            log(`sent ${nameee}`)
        }
        online = true;
      } 
    } catch (error) {
      online = false;
    }
  };
  
  const readSubs = () => {
    const subscribers = JSON.parse(fs.readFileSync('subscribers.json'));
    return subscribers;
  };
  
  const addToSubs = (chatId, subscriber) => {
    chatId = chatId.toString();
    const subscribers = readSubs();
    if (!(chatId in subscribers)) {
      subscribers[chatId] = subscriber;
      fs.writeFileSync('subscribers.json', JSON.stringify(subscribers));
      return true;
    } else {
      return false;
    }
  };

  const remFromSubs = (chatId) => {
    chatId = chatId.toString();
    const subscribers = readSubs();
    if (chatId in subscribers) {
      delete subscribers[chatId];
      fs.writeFileSync('subscribers.json', JSON.stringify(subscribers));
      return true;
    } else {
      return false;
    }
  };

  const getUname = (id, name) => (name ? `@${name}` : `tg://user?id=${id}`);

  const log = async (message) => {
    try {
      await fs.promises.appendFile('msg.log', message + '\n');
    } catch (error) {
      console.error(error);
    }
  }; 
  

  const runCheckStreamStatus = () => {
        setInterval(() => {
          checkStreamStatus();
        }, 60 * 1000); // Run every minute
  };
  
  runCheckStreamStatus();

