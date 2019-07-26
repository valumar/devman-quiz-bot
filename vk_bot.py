import os
import json

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

import redis

from dotenv import load_dotenv
from text_utils import load_data, get_random_question, spellcheck, compare


def init_keyboard():
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.DEFAULT)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.NEGATIVE)
    return keyboard


def init_user_data(user_id):
    user_data = {"user_id": user_id}
    if r.get(user_id):
        user_data = json.loads(r.get(user_id))
    return user_data


def send_message(event, vk_api, message):
    keyboard = init_keyboard()
    vk_api.messages.send(
        peer_id=123456,
        user_id=event.user_id,
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def new_question(event, vk_api):
    data = load_data('dict.json')
    user_data = init_user_data(event.user_id)
    quest = get_random_question(data)
    question = quest['Вопрос']
    user_data['quest'] = quest

    r.set(user_data['user_id'], json.dumps(user_data))

    message = f'Отправляем новый вопрос\n{question}'
    send_message(event, vk_api, message)


def check_answer(event, vk_api):
    user_data = init_user_data(event.user_id)
    if 'quest' in user_data:
        quest = user_data['quest']
        answer = quest['Ответ'][0]
        desc = quest['Ответ'][1]
        if 'score' in user_data:
            score = user_data['score']
        else:
            score = 0
        if compare(spellcheck(event.text), answer):
            message = f'Похоже на правду!\nПравильный ответ: \n{answer}\n{desc}'
            score += 1
            user_data['score'] = score
            r.set(event.user_id, json.dumps(user_data))
        else:
            message = 'Неверно! Хотите сдаться или попробовать ответить ещё раз?'
    else:
        message = 'Hi!'
    send_message(event, vk_api, message)


def givup(event, vk_api):
    user_data = init_user_data(event.user_id)
    if 'quest' in user_data:
        quest = user_data['quest']
        answer = quest['Ответ'][0]
        desc = quest['Ответ'][1]
        message = f'Вы сдались \nПравильный ответ: \n{answer} \n{desc}'
    else:
        message = 'Hi!'
    send_message(event, vk_api, message)


def score(event, vk_api):
    user_data = init_user_data(event.user_id)
    if 'score' in user_data:
        score = user_data['score']
    else:
        score = 0
    message = f'ваш счёт: {score}'
    send_message(event, vk_api, message)


if __name__ == "__main__":
    load_dotenv()
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=1)

    vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Новый вопрос":
                new_question(event, vk_api)
            elif event.text == "Сдаться":
                givup(event, vk_api)
            elif event.text == "Мой счёт":
                score(event, vk_api)
            else:
                check_answer(event, vk_api)

