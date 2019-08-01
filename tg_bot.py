import json
import logging
import os
import redis

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from text_utils import load_data, get_random_question, check_spelling, compare

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY = range(2)

reply_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(bot, update):
    update.message.reply_text(
        "Приветствую тебя на викторине ЧГК!",
        reply_markup=markup)

    return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def init_user_data(bot, update, user_data):
    chat_id = update.message.chat_id
    if r.get(chat_id):
        user_data = json.loads(r.get(chat_id))
    return user_data


def handle_new_question_request(bot, update, user_data):
    user_data = init_user_data(bot, update, user_data)
    user_data['chat_id'] = update.message.chat_id
    update.message.reply_text('Отправляем новый вопрос')
    data = load_data('dict.json')
    user_data['quest'] = get_random_question(data)
    question = user_data['quest']['Вопрос']
    championat = user_data['quest']['Чампионат']
    answer = user_data['quest']['Ответ'][0]
    desc = user_data['quest']['Ответ'][1]

    r.set(user_data['chat_id'], json.dumps(user_data))
    logger.info(f"{question}, {answer}, {user_data['chat_id']}")
    update.message.reply_text(f'Вопрос из пакета:\n {championat}')
    update.message.reply_text(question, reply_markup=markup)

    return TYPING_REPLY


def handle_solution_attempt(bot, update, user_data):
    text = update.message.text
    user_data = init_user_data(bot, update, user_data)
    chat_id = user_data['chat_id']
    if r.get(chat_id):
        quest = user_data['quest']
        answer = quest['Ответ'][0]
        desc = quest['Ответ'][1]
        if 'send_score' in user_data:
            score = user_data['send_score']
        else:
            score = 0
        if compare(check_spelling(text), answer):
            update.message.reply_text(f'Похоже на правду! \nПравильный ответ: \n{answer} \n{desc}', reply_markup=markup)
            score += 1
            user_data['send_score'] = score
            r.set(chat_id, json.dumps(user_data))
            return CHOOSING
        else:
            update.message.reply_text('Неверно! Хотите сдаться или попробовать ответить ещё раз?', reply_markup=markup)
            return TYPING_REPLY
    else:
        return CHOOSING


def giveup(bot, update, user_data):
    """Return the answer for question and then return user to main menu"""
    user_data['chat_id'] = update.message.chat_id
    chat_id = user_data['chat_id']
    quest = json.loads(r.get(chat_id))['quest']
    answer = quest['Ответ'][0]
    desc = quest['Ответ'][1]
    update.message.reply_text(f'Вы сдались \nПравильный ответ: \n{answer} \n{desc}', reply_markup=markup)

    return CHOOSING


def send_score(bot, update, user_data):
    """Return user score and then return user to main menu"""
    user_data =init_user_data(bot, update, user_data)
    if 'send_score' in user_data:
        score = user_data['send_score']
    else:
        score = 0
    update.message.reply_text(f'Ваш счет: {score}', reply_markup=markup)

    return CHOOSING


def start_bot(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(
        token,
        request_kwargs={'proxy_url': os.getenv('TELEGRAM_HTTPS_PROXY')}
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      # в случае перезагрузки бота продолжаем диалог
                      RegexHandler('^Новый вопрос$',
                                   handle_new_question_request,
                                   pass_user_data=True
                                   ),
                      RegexHandler('^Сдаться$', giveup, pass_user_data=True),
                      RegexHandler('^Мой счет$', send_score, pass_user_data=True),
                      MessageHandler(Filters.text,
                                     handle_solution_attempt,
                                     pass_user_data=True),
                      ],

        states={
            CHOOSING: [RegexHandler('^Новый вопрос$',
                                    handle_new_question_request,
                                    pass_user_data=True
                                    ),
                       RegexHandler('^Сдаться$', giveup, pass_user_data=True),
                       RegexHandler('^Мой счет$', send_score, pass_user_data=True)
                       ],


            TYPING_REPLY: [RegexHandler('^Сдаться$', giveup, pass_user_data=True),
                           RegexHandler('^Мой счет$', send_score, pass_user_data=True),
                           MessageHandler(Filters.text,
                                          handle_solution_attempt,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[RegexHandler('^Сдаться$', giveup, pass_user_data=True),
                   RegexHandler('^Мой счет$', send_score, pass_user_data=True)
                   ]
    )

    dp.add_handler(conv_handler)

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
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    bot_token = os.getenv("TELEGRAM_TOKEN")
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0)
    start_bot(bot_token)
