import logging

from collections import defaultdict

import aiohttp

from aiohttp.web_exceptions import HTTPError

from core.user.user_events import DEFAULT_MODE, Event, VkEventType, VkLongpollMode
from core.vk_api import VkApi


class VkLongPoll(object):
    """ Класс для работы с longpoll-сервером

    `Подробнее в документации VK API <https://vk.ru/dev/using_longpoll>`__.

    :param vk: объект :class:`VkApi`
    :param wait: время ожидания
    :param mode: дополнительные опции ответа
    :param preload_messages: предзагрузка данных сообщений для
        получения ссылок на прикрепленные файлы
    :param group_id: идентификатор сообщества
        (для сообщений сообщества с ключом доступа пользователя)
    """

    __slots__ = (
        'vk', 'wait', 'mode', 'preload_messages', 'group_id',
        'url', 'session',
        'key', 'server', 'ts', 'pts', 'lgr'
    )

    #: Класс для событий
    DEFAULT_EVENT_CLASS = Event

    #: События, для которых можно загрузить данные сообщений из API
    PRELOAD_MESSAGE_EVENTS = [
        VkEventType.MESSAGE_NEW,
        VkEventType.MESSAGE_EDIT
    ]

    def __init__(self, vk: VkApi, wait=25, mode=DEFAULT_MODE,
                 preload_messages=False, group_id=None):
        self.vk = vk
        self.wait = wait
        self.mode = mode.value if isinstance(mode, VkLongpollMode) else mode
        self.preload_messages = preload_messages
        self.group_id = group_id
        self.lgr = logging.getLogger(self.__class__.__name__)

        self.url = None
        self.key = None
        self.server = None
        self.ts = None
        self.pts = None

        self.session = aiohttp.ClientSession()

    def _parse_event(self, raw_event):
        return self.DEFAULT_EVENT_CLASS(raw_event)

    async def update_longpoll_server(self, update_ts=True):
        values = {
            'lp_version': '3',
            'need_pts': 1
        }
        if self.group_id:
            values['group_id'] = self.group_id

        response = await self.vk.method('messages.getLongPollServer', values)
        if not (response := response.get('response')):
            text = "Get longpoll server failed: " + str(response)
            logging.error(text)
            raise HTTPError(text=text)

        self.key = response['key']
        self.server = response['server']

        self.url = f'https://{self.server}'

        if update_ts:
            self.ts = response['ts']
            self.pts = response.get('pts')

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
            'mode': self.mode,
            'version': 3
        }

        response = await self.vk.send(self.url, values, self.wait)

        if 'failed' not in response:
            self.ts = response['ts']
            self.pts = response.get('pts')

            events = [
                self._parse_event(raw_event)
                for raw_event in response['updates']
            ]

            if self.preload_messages:
                await self.preload_message_events_data(events)

            return events

        elif response['failed'] == 1:
            self.ts = response['ts']

        elif response['failed'] == 2:
            await self.update_longpoll_server(update_ts=False)

        elif response['failed'] == 3:
            await self.update_longpoll_server()

        return []

    async def preload_message_events_data(self, events):
        """ Предзагрузка данных сообщений из API

        :type events: list of Event
        """
        message_ids = set()
        event_by_message_id = defaultdict(list)

        for event in events:
            if event.type in self.PRELOAD_MESSAGE_EVENTS:
                message_ids.add(event.message_id)
                event_by_message_id[event.message_id].append(event)

        if not message_ids:
            return

        messages_data = await self.vk.method(
            'messages.getById',
            {'message_ids': message_ids}
        )

        for message in messages_data['items']:
            for event in event_by_message_id[message['id']]:
                event.message_data = message
