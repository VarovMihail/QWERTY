import vk_api
from pprint import pprint
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from config import ACCESS_TOKEN, tok
from vkinder_class import VKinder
import psycopg2


conn = psycopg2.connect(dbname='vkkinder', user='postgres', password='ENot3112', host='localhost')

keyboard = VkKeyboard(inline=True)
keyboard.add_button('start', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('next', color=VkKeyboardColor.PRIMARY)
keyboard.add_button('like', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('list', color=VkKeyboardColor.SECONDARY)
keyboard.add_button('stop', color=VkKeyboardColor.NEGATIVE)

session = vk_api.VkApi(token=ACCESS_TOKEN)  # Подключаем токен и longpoll
photos = VkUpload(session)  # переменная для загрузки фото
vk = session.get_api()
longpoll = VkLongPoll(session)  # сообщаем что хотим исп именно подключение через VkLongPoll


def replay(id, text):  # Создадим функцию для ответа на сообщения в лс группы
    session.method('messages.send', {'user_id': id,
                                     'message': text,
                                     'random_id': 0,
                                     'attachment': ','.join(attachments),
                                     'keyboard': keyboard.get_keyboard()
                                     })


for event in longpoll.listen():  # Слушаем longpoll(Сообщения)
    attachments = []
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message = event.text.lower()
        id = event.user_id
        print(type(id))
        with conn.cursor() as cursor:
            cursor.execute(f'select id from users;')
            id_list = [i[0] for i in cursor.fetchall()]
            print(id_list)
            if id not in id_list:
                cursor.execute(f'INSERT INTO users (id) VALUES ({id})')
                conn.commit()

        if message == 'привет':
            replay(id, 'Привет, укажите через запятую интересующий вас пол(м/ж), город, минимальный возраст, максимальный возраст')
        elif len(message.split(',')) == 4:
            replay(id, 'Сейчас поищу')
            replay(id, 'start - начать\n'
                       'next - следующий человек\n'
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

        elif message in ('start', 'next', 'like', 'stop', 'list'):
            user_data = next(items)
            first_name, last_name, link = user_data[0].replace('\n', '').split(' ')
            user_name = first_name + ' ' + last_name
            #user_id = link.split('/')[-1][2:]

            print(user_data)
            print(user_name, link)

            if message == 'start' or message == 'next':
                with conn.cursor() as cursor:
                    cursor.execute(f'SELECT link FROM black_list ')
                    cursor_data = cursor.fetchall()
                    print('-' * 30)
                    print((cursor_data))
                    print(cursor)
                    print('-' * 30)

                    if cursor_data:
                        print(type(id))
                        cursor.execute(f'SELECT link FROM black_list WHERE id = {id}')
                        print('*********')
                        for el in [i[0] for i in cursor.fetchall()]:
                            if el != link:
                                if len(user_data[1]) != 0:
                                    attachments = user_data[1]
                                    replay(id, user_data[0])
                                    cursor.execute(
                                        f'INSERT INTO black_list (user_name, link, id) VALUES '
                                        f'({user_name}, {link}, {id});'
                                    )
                                else:
                                    replay(id, f'{user_data[0]}\nНа странице нет фото')
                                    cursor.execute(
                                        f'INSERT INTO black_list (user_name, link, id) VALUES '
                                        f'({user_name}, {link}, {id});'
                                    )
                            else:
                                continue
                    else:
                        if len(user_data[1]) != 0:
                            attachments = user_data[1]
                            replay(id, user_data[0])
                            print(user_name)
                            print(link)
                            print(id)
                            print(type(user_name), type(link), type(id))
                            with conn.cursor() as cursor:
                                cursor.execute(f'INSERT INTO black_list (user_name, link, id) VALUES ({user_name}, {link}, {id});')
                                conn.commit()
                        else:
                            replay(id, f'{user_data[0]}\nНа странице нет фото')
                            cursor.execute(
                                f'INSERT INTO black_list (user_name, link, id) VALUES '
                                f'({user_name}, {link}, {id});'
                            )
            elif message == 'like':
                first_name, last_name, link = user_data[0].replace('\n', '').split(' ')
                with conn.cursor() as cursor:
                    cursor.execute(
                        f'INSERT INTO like_list (user_name, link, user_id) VALUES ({first_name} {last_name}, {link}, {id});'
                    )
                replay(id, "Пользователь добавлен в избранное")
            elif message == 'list':
                with conn.cursor() as cursor:
                    cursor.execute(f'SELECT link FROM like_list WHERE id = {id}')
                    for el in cursor:
                        replay(id, el)
            elif message == 'stop':
                break
        else:
            replay(id, 'Меня к такому не готовили')
conn.close()