import json
import random
import logging
import os
import redis
import pymorphy2
import telegram
import requests

from string import punctuation
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    # filename='log.log'
)


def load_data(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def get_random_question(data):
    random_champ = random.choice(list(data.values()))
    random_question = random.choice(random_champ)
    return random_question


def normalize(sentence):
    morph = pymorphy2.MorphAnalyzer()
    for character in punctuation:
        sentence = sentence.replace(character, " ")
    sentence = sentence.split()
    normalized_sentence = []
    for word in sentence:
        normalized_sentence.append(morph.parse(word)[0].normal_form)
    return set(normalized_sentence)


def compare(answer, ethalon):
    normalized_answer = normalize(answer)
    normalized_ethalon = normalize(ethalon)
    p = normalized_ethalon - normalized_answer

    result = False
    if len(p) <= .5 * len(normalized_ethalon):
        result = True
    return result

# TODO: Обрапотка очпяток и громотищеских ошипок


def spellcheck(sentence):
    url = "https://speller.yandex.net/services/spellservice.json/checkTexts"
    payload = {
        "text": sentence
    }
    response = requests.get(url, params=payload)
    if response.ok:
        checked_sentence = " ".join(i['s'][0] for i in response.json()[0])
        return checked_sentence
    else:
        return sentence


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
    update.message.reply_text(text="...", reply_markup=reply_markup)


def echo(bot, update):
    """Echo the user message."""
    chat_id = update.message.chat_id
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    answer, desc = '', ''
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    # update.message.reply_text(text='.', reply_markup=reply_markup)
    if r.get(chat_id):
        quest = json.loads(r.get(chat_id))
        answer = quest['Ответ'][0]
        desc = quest['Ответ'][1]
    if update.message.text == 'Новый вопрос':
        update.message.reply_text('Отправляем новый вопрос')
        quest = get_random_question(data)
        question = quest['Вопрос']
        answer = quest['Ответ'][0]
        desc = quest['Ответ'][1]
        r.set(chat_id, json.dumps(quest))
        print(question, answer, chat_id)
        update.message.reply_text(question)
    elif update.message.text == 'Сдаться':
        update.message.reply_text('Вы сдались')
        update.message.reply_text(f'Правильный ответ: \n{answer}')
        update.message.reply_text(desc)
    elif update.message.text == 'Мой счет':
        update.message.reply_text('Ваш счет: ')
    elif compare(spellcheck(update.message.text), answer):
        update.message.reply_text('Похоже на правду!')
        update.message.reply_text(f'Правильный ответ: \n{answer}')
        update.message.reply_text(desc)
    else:
        update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def start_bot(token, data):
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_TOKEN")
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0)
    data = load_data('dict.json')
    start_bot(bot_token, data)

