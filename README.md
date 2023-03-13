#  twitch-notify-telegram

#### Telegram бот на NodeJS для уведомления зрителей о начавшемся стриме на Twitch. 

## Установка:
[Создать приложение Twitch Application](https://dev.twitch.tv/console/apps/create)

[Создать бота через BotFather в Telegram](https://telegram.me/BotFather)

```bash
git clone https://github.com/ch4og/twitch-notify-telegram
cd twitch-notify-telegram
npm i
touch msg.log
echo "{}" > subscribers.json
```

#### Отредактировать .env 

- ```TW_SECRET``` На самом деле это токен (https://twitchtokengenerator.com/)
- ```TW_CLIENT```
- ```STREAMER```
- ```TG_API```
- ```LINK``` 

```LINK - ссылка на стримера в информации.```

#### Запуск через node
- Например ```node ./app.js``` или ```pm2 start ./app.js```
