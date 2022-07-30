import vk_api
from pprint import pprint
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from config import ACCESS_TOKEN, tok
from vkinder_class import VKinder
import psycopg2

# from funk import replay, insert_into_black_list, insert_into_like_list, next_person

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


def replay(id, text):  # Ответ плюс клавиатура
    session.method('messages.send', {'user_id': id,
                                     'message': text,
                                     'random_id': 0,
                                     'attachment': ','.join(attachments),
                                     'keyboard': keyboard.get_keyboard()
                                     })


def replay_without_keyboard(id, text):  # Ответ без клавиатуры
    session.method('messages.send', {'user_id': id,
                                     'message': text,
                                     'random_id': 0,
                                     'attachment': ','.join(attachments)})


def insert_into_black_list(user_name, link, id):
    cursor.execute('''INSERT INTO black_list (user_name, link, id)
                    VALUES (%s, %s, %s);''', (user_name, link, id))
    conn.commit()


def insert_into_like_list(user_name, link, id):
    cursor.execute('''INSERT INTO like_list (user_name, link, id)
                    VALUES (%s, %s, %s);''', (user_name, link, id))
    conn.commit()


def next_person(items):  # следующий человек(меняется только после start/next)
    try:
        user_data = next(items)
        first_name, last_name, link = user_data[0].replace('\n', '').split(' ')
        user_name = first_name + ' ' + last_name
    except StopIteration:
        print('КОНЕЦ')
        user1 = VKinder(tok, gender, city, min_age, max_age, 5)
        my_list = user1.search()
        items = iter(my_list)
        user_data = next(items)
        first_name, last_name, link = user_data[0].replace('\n', '').split(' ')
        user_name = first_name + ' ' + last_name
        return user_data, user_name, link
    return user_data, user_name, link


for event in longpoll.listen():  # Слушаем longpoll(Сообщения)
    with conn.cursor() as cursor:
        attachments = []
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message = event.text.lower()
            id = event.user_id
            cursor.execute(f'select id from users;')
            id_list = [i[0] for i in cursor.fetchall()]
            print('Это id_list\n', id_list)
            if id not in id_list:
                cursor.execute('''INSERT INTO users (id) VALUES (%s);''', (id,))
                conn.commit()

            if message == 'привет':
                replay_without_keyboard(id, 'Укажите пол/город/минимальный возраст/максимальный возраст\n'
                                            'Должно получиться вот так:\nм/Санкт-Петербург/30/40')
            elif len(message.split('/')) == 4:
                replay_without_keyboard(id, 'Сейчас поищу')

                gender, city, min_age, max_age = [i.strip() for i in message.split('/')]
                user1 = VKinder(tok, gender, city, min_age, max_age, 5)
                my_list = user1.search()
                if not my_list:
                    replay_without_keyboard(id, 'Неверный запрос, попробуйте еще раз')
                else:
                    items = iter(my_list)
                    print('Это items\n', items)
                    print('Это my_list\n', my_list)
                    replay(id, 'start - начать\n'
                               'next - следующий человек\n'
                               'like - добавить в избранное\n'
                               'stop - остановить поиск\n'
                               'list - показать список избранных\n')
            elif message == 'start' or message == 'next':
                user_data, user_name, link = next_person(items)  # СЛЕДУЮЩИЙ ЧЕЛОВЕК ИЗ СПИСКА
                print(user_data)
                with conn.cursor() as cursor:
                    cursor.execute(f'SELECT link FROM black_list ')
                    link_list = cursor.fetchall()
                    if link_list:  # если в таблице black_list есть ссылки(она не пустая)
                        cursor.execute('''SELECT link FROM black_list WHERE id = %s;''', (id,))
                        link_list = [i[0] for i in cursor.fetchall()]
                        print(f'{link_list = }')
                        if link not in link_list:  # если ссылки нет в черном списке
                            if len(user_data[1]) != 0:
                                attachments = user_data[1]
                                replay(id, user_data[0])
                                insert_into_black_list(user_name, link, id)

                            else:
                                replay(id, f'{user_data[0]}\nНа странице нет фото')
                                insert_into_black_list(user_name, link, id)
                        else:  # если ссылка есть в черном списке
                            while True:
                                user_data, user_name, link = next_person(items)  # СЛЕДУЮЩИЙ ЧЕЛОВЕК ИЗ СПИСКА
                                if link not in link_list:
                                    if len(user_data[1]) != 0:
                                        insert_into_black_list(user_name, link, id)
                                        attachments = user_data[1]
                                        replay(id, user_data[0])
                                        break

                    else:  # если таблица black_list пустая
                        if len(user_data[1]) != 0:
                            attachments = user_data[1]
                            replay(id, user_data[0])
                            insert_into_black_list(user_name, link, id)
                        else:
                            replay(id, f'{user_data[0]}\nНа странице нет фото')
                            insert_into_black_list(user_name, link, id)
            elif message == 'like':
                cursor.execute('''SELECT link FROM like_list WHERE id = %s;''', (id,))
                link_like_list = [i[0] for i in cursor.fetchall()]
                if link not in link_like_list:
                    insert_into_like_list(user_name, link, id)
                    replay(id, "Пользователь добавлен в избранное")
                else:
                    replay(id, "Пользователь уже был добавлен ранее")
            elif message == 'list':
                cursor.execute('''SELECT link FROM like_list WHERE id = %s;''', (id,))
                like_list = cursor.fetchall()
                print(like_list)
                if like_list:
                    for el in like_list:
                        replay(id, el)
                else:
                    replay(id, 'Ваш список пуст')
            elif message == 'stop':
                replay(id, "Чтобы продолжить нажмите START")
                # break
            else:
                replay_without_keyboard(id, 'Меня к такому не готовили\n Лучше напишите привет.')
