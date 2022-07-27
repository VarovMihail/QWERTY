import vk_api
from pprint import pprint
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from config import ACCESS_TOKEN
from vkinder_class import VKinder
from config import tok
from time import sleep
from vk_api.keyboard import VkKeyboard

keyboard = VkKeyboard(inline=True)
keyboard.add_button('start',color=VkKeyboardColor.PRIMARY)
keyboard.add_button('skip',color=VkKeyboardColor.SECONDARY)
keyboard.add_button('like',color=VkKeyboardColor.POSITIVE)
keyboard.add_button('list',color=VkKeyboardColor.SECONDARY)
keyboard.add_button('stop',color=VkKeyboardColor.NEGATIVE)
# Подключаем токен и longpoll
session = vk_api.VkApi(token=ACCESS_TOKEN)
photos = VkUpload(session) # переменная для загрузки фото
vk = session.get_api()
longpoll = VkLongPoll(session) # сообщаем что хотим исп именно подключение через VkLongPoll

# Создадим функцию для ответа на сообщения в лс группы
def replay(id, text):
    session.method('messages.send', {'user_id': id,
                                     'message': text,
                                     'random_id': 0,
                                     'attachment': ','.join(attachments),
                                     'keyboard': keyboard.get_keyboard()
                                     })

# Слушаем longpoll(Сообщения)
for event in longpoll.listen():
    attachments = []
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message = event.text.lower()
        id = event.user_id
        if message == 'привет':
            replay(id, 'Привет, укажите через запятую интересующий вас пол(м/ж), город, минимальный возраст, максимальный возраст')

        elif len(message.split(',')) == 4:
            replay(id, 'Сейчас поищу')
            sleep(2)

            replay(id, 'start - начать\n'
                       'skip - пропустить человека\n'
                       'like - добавить в избранное\n'
                       'stop - остановить поиск\n'
                       'list - показать список избранных\n'
                       'Введите команду: ')
            gender, city, min_age, max_age = [i.strip() for i in message.split(',')]
            user1 = VKinder(tok, gender, city, min_age, max_age)
            my_list = user1.search()
            pprint(my_list)
            items = iter(my_list)
            print(items)

        elif message in ('start', 'skip', 'like', 'stop', 'list'):
            user_data = next(items)
            print(user_data)
            if message == 'start':
                if len(user_data) != 0:
                    attachments = user_data[1]
                    replay(id, user_data[0])
                else:
                    replay(id, 'На странице нет фото')
            elif message == 'skip':
                if len(user_data) != 0:
                    attachments = user_data[1]
                    replay(id, user_data[0])
                else:
                    replay(id, 'На странице нет фото')

            elif message == 'like':
                messages = event.messages.get(count=1)
                last = messages['items'][0]['id']
                replay(id, last)
            elif message == 'stop':
                break
            elif message == 'list':
                pass
        else:
            replay(id, 'Меня к такому не готовили')
