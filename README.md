#  twitch-notify-telegram

#### Telegram бот на ~Python~ NodeJS для уведомления зрителей о начавшемся стриме на Twitch. 

1. [Создать приложение Twitch Application](https://dev.twitch.tv/console/apps/create)
2. [Создать бота через BotFather в Telegram](https://telegram.me/BotFather)

3. ```git clone https://github.com/ch4og/twitch-notify-telegram```

4. ```cd twitch-notify-telegram```

5. ```npm i```

6. ```touch msg.log```

7. ```echo "{}" > subscribers.json```

8. отредактировать .env 

- TW_OAUTH ```(Twitch Secret)```
- TW_CLIENT 
- STREAMER 
- TG_API 
- LINK ```(Ссылка на стримера в информации)```

9. Использовать любой способ запуска node скрипта
- Например ```node ./app.js``` или ```pm2 start ./app.js```
