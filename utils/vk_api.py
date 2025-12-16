import configparser

import aiohttp
import aiohttp_socks
import json

from config import Config


class VkApi:
    def __init__(self):
        config = Config()
        self.session = aiohttp.ClientSession()
        self.proxy = config.proxy
        self.token = config.token
        self.group_id = config.group_id
        self.longpoll_server = None
        self.longpoll_key = None
        self.longpoll_ts = None

    async def start_longpoll(self):
        url = 'https://api.vk.com/method/messages.getLongPollServer'
        params = {
            'access_token': self.token,
            'v': '5.199',
            'group_id': self.group_id,
        }
        async with self.session.get(url, params=params, proxy=self.proxy) as response:
            data = await response.json()
            self.longpoll_server = data['response']['server']
            self.longpoll_key = data['response']['key']
            self.longpoll_ts = data['response']['ts']
            print(data)

    async def get_updates(self):
        if not self.longpoll_server or not self.longpoll_key or not self.longpoll_ts:
            await self.start_longpoll()

        url = f"https://{self.longpoll_server}?act=a_check&key={self.longpoll_key}&ts={self.longpoll_ts}&wait=5"
        async with self.session.get(url, proxy=self.proxy) as response:
            data = await response.json()
            if 'ts' in data:
                self.longpoll_ts = data['ts']
            return data.get('updates', [])

    async def send_message(self, user_id, message, keyboard=None):
        url = 'https://api.vk.com/method/messages.send'
        params = {
            'access_token': self.token,
            'v': '5.199',
            'user_id': user_id,
            'message': message,
            'random_id': 0
        }
        if keyboard:
            params['keyboard'] = json.dumps(keyboard)
        async with self.session.get(url, params=params, proxy=self.proxy) as response:
            return await response.json()

    async def close(self):
        await self.session.close()
