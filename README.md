# Бот Викторина Что?Где?Когда? для Telegram и VK Groups

Бот Викторина Что?Где?Когда?


![Бот Викторина Что?Где?Когда?](gif/GIF.gif)


### Установка и настройка

Данный проект состоит из нескольких частей:

- модуль загрузки словаря с вопросами `load_data.py`
- боты:
    - для Telegram
    - для VK Groups

#### 
У вас должен быть установлен python3 
крайне рекомендуется использовать [виртуальное окружение](https://docs.python.org/3/library/venv.html) для изоляции проекта. 
Используйте `pip` (или `pip3`, если возникает конфликт с Python2) для инсталляции зависимостей:

```bash
pip install -r requirements.txt
```
Также возможно развернуть этого бота на Heroku: 
просто создайте новое приложение на Heroku и подключите его к репозиторию GitHub.

Помимо этого Вам необходим доступ к серверу Redis

#### Настройики Бота Викторины Что?Где?Когда? для Telegram и VK Groups
Вам необходимо зарегистрировать Telegram Bot через [@BotFather] (https://telegram.me/botfather) и получить TELEGRAM_TOKEN и TELEGRAM_CHAT_ID (для этого используйте [@userinfobot] (https://telegram.me/userinfobot))
После этого скопируйте файл `.env-example` в` .env` и вставьте вашу информацию в поля:
```dotenv
TELEGRAM_TOKEN=
```

#### Настройики Бота Викторины Что?Где?Когда? для VK Groups
Для правильного использования вы должны получить учетную запись ВКонтакте. Вам необходимо создать [VK Group] (https://vk.com/groups_create) и создать ключ API для группы в настройках группы (`https: //vk.com/your_group? Act = tokens`)
Вставьте свою информацию в `.env`:
```dotenv
VK__TOKEN=your_vk_group_token
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org] (https://dvmn.org/).