import logging
from typing import Optional

import aiohttp

from aiohttp.web_exceptions import HTTPError

from core.bot.bot_events import VkBotCallbackEvent, VkBotEvent, VkBotEventType, VkBotMessageEvent
from core.vk_api import VkApi

CHAT_START_ID = int(2E9)


class VkBotLongPoll(object):
    """ Класс для работы с Bots Long Poll сервером

    `Подробнее в документации VK API <https://vk.ru/dev/bots_longpoll>`__.

    :param vk: объект :class:`VkApi`
    :param group_id: id группы (если None, загружается автоматически)
    :param wait: время ожидания
    """

    __slots__ = (
        'vk', 'wait', 'group_id',
        'url', 'session',
        'key', 'server', 'ts',
        '_on_bot_info_read',
    )

    #: Классы для событий по типам
    CLASS_BY_EVENT_TYPE = {
        VkBotEventType.MESSAGE_NEW.value: VkBotMessageEvent,
        VkBotEventType.MESSAGE_REPLY.value: VkBotMessageEvent,
        VkBotEventType.MESSAGE_EDIT.value: VkBotMessageEvent,
        VkBotEventType.MESSAGE_EVENT.value: VkBotCallbackEvent,
    }

    #: Класс для событий
    DEFAULT_EVENT_CLASS = VkBotEvent

    def __init__(self, vk, group_id=None, wait=25):
        self.vk: VkApi = vk
        self.group_id = group_id
        self.wait = wait
        self._on_bot_info_read = None

        self.url = None
        self.key = None
        self.server = None
        self.ts = None

        self.session = aiohttp.ClientSession()

    def on_bot_info_read(self, callback):
        """Зарегистрировать callback, который будет вызван после получения
        информации о боте (screen_name, name, id)."""
        self._on_bot_info_read = callback

    async def _load_group_id(self) -> Optional[int]:
        me = await self.vk.method("groups.getById", {})
        if "response" in me:
            me = me["response"]['groups'][0]
            if self._on_bot_info_read:
                await self._on_bot_info_read(
                    me.get("screen_name"),
                    me.get("name"),
                    me.get("id"),
                )
            return me.get("id")
        return None

    def _parse_event(self, raw_event):
        event_class = self.CLASS_BY_EVENT_TYPE.get(
            raw_event['type'],
            self.DEFAULT_EVENT_CLASS
        )
        return event_class(raw_event)

    async def update_longpoll_server(self, update_ts=True):
        if not self.group_id:
            self.group_id = await self._load_group_id()

        values = {
            'lp_version': '3',
            'need_pts': 1,
            'group_id': self.group_id,
        }

        response = await self.vk.method('groups.getLongPollServer', values)
        if not (response := response.get('response')):
            text = "Get longpoll server failed: " + str(response)
            logging.error(text)
            raise HTTPError(text=text)

        self.key = response['key']
        self.server = response['server']

        self.url = self.server

        if update_ts:
            self.ts = response['ts']

        logging.debug(f"Longpoll server updated. Server '{self.url}' key: {self.key}")

    async def get_events(self):
        """ Получить события от сервера один раз

        :returns: `list` of :class:`Event`
        """
        if not self.url:
            raise RuntimeError('Longpoll server not initialized (update)')
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
        }

        response = await self.vk.send(self.url, values, self.wait)

        if 'failed' not in response:
            self.ts = response['ts']

            events = [
                self._parse_event(raw_event)
                for raw_event in response['updates']
            ]

            return events

        elif response['failed'] == 1:
            self.ts = response['ts']

        elif response['failed'] == 2:
            await self.update_longpoll_server(update_ts=False)

        elif response['failed'] == 3:
            await self.update_longpoll_server()

        return []
