import os

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from dotenv import load_dotenv


def echo(event, vk_api):

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.DEFAULT)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.NEGATIVE)

    vk_api.messages.send(
        peer_id=123456,
        user_id=event.user_id,
        message=event.text,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


if __name__ == "__main__":
    load_dotenv()
    vk_session = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)
