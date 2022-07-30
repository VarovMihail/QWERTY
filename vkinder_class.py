import requests
from config import tok
from pprint import pprint


class VKinder:
    offset = 0

    def __init__(self, user_token, gender, city, min_age, max_age, count):
        self.count = count
        self.user_token = user_token
        self.params = {'access_token': self.user_token, 'v': '5.131'}
        self.base_url = 'https://api.vk.com/method/'
        self.gender = gender
        self.city = city
        self.min_age = min_age
        self.max_age = max_age

    def get_top_photo(self, id):
        result = {}
        method = 'photos.get'
        params = {'owner_id': id,
                  'album_id': 'profile',
                  'extended': 1}
        res = requests.get(self.base_url + method, params={**params, **self.params}).json()
        # pprint(res)

        for el in res['response']['items']:
            result[f"photo{el['owner_id']}_{el['id']}"] = el['likes']['count']
        user_photo = [photo for photo in sorted(result, key=result.get, reverse=True)[:3]]
        # result[el['sizes'][-1]['url']] = el[f'likes']['count']
        return user_photo

    def search(self):
        if self.gender.lower() in ['мужской', 'мужчина', 'муж', 'м']:
            self.gender = 2
        elif self.gender.lower() in ['женский', 'женщина', 'жен', 'ж']:
            self.gender = 1
        method = 'users.search'
        params = {'count': self.count,
                  'offset': VKinder.offset,
                  'can_access_closed': True,
                  'age_from': self.min_age,
                  'age_to': self.max_age,
                  'hometown': self.city,
                  'sex': self.gender,
                  'fields': 'home_town'}

        res = requests.get(self.base_url + method, params={**params, **self.params}).json()
        VKinder.offset += self.count
        # pprint(res)
        l = []
        for el in res['response']['items']:

            if el['can_access_closed']:
                print(el)
                first_name = el["first_name"]
                last_name = el["last_name"]
                owner_id = el["id"]

                l.append([f'{first_name} {last_name}\n https://vk.com/id{owner_id}\n', self.get_top_photo(owner_id)])
        return l
