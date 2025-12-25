# -*- coding: utf-8 -*-
"""
:authors: deker104, python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""
import logging

import aiohttp
from aiohttp.web_exceptions import HTTPError

from core.bot.bot_events import VkBotEventType, VkBotEvent, VkBotMessageEvent

CHAT_START_ID = int(2E9)


class VkBotLongPoll(object):
    """ Класс для работы с Bots Long Poll сервером

    `Подробнее в документации VK API <https://vk.ru/dev/bots_longpoll>`__.

    :param vk: объект :class:`VkApi`
    :param group_id: id группы
    :param wait: время ожидания
    """

    __slots__ = (
        'vk', 'wait', 'group_id',
        'url', 'session',
        'key', 'server', 'ts'
    )

    #: Классы для событий по типам
    CLASS_BY_EVENT_TYPE = {
        VkBotEventType.MESSAGE_NEW.value: VkBotMessageEvent,
        VkBotEventType.MESSAGE_REPLY.value: VkBotMessageEvent,
        VkBotEventType.MESSAGE_EDIT.value: VkBotMessageEvent,
    }

    #: Класс для событий
    DEFAULT_EVENT_CLASS = VkBotEvent

    def __init__(self, vk, group_id, wait=25):
        self.vk = vk
        self.group_id = group_id
        self.wait = wait

        self.url = None
        self.key = None
        self.server = None
        self.ts = None

        self.session = aiohttp.ClientSession()

    def _parse_event(self, raw_event):
        event_class = self.CLASS_BY_EVENT_TYPE.get(
            raw_event['type'],
            self.DEFAULT_EVENT_CLASS
        )
        return event_class(raw_event)

    async def update_longpoll_server(self, update_ts=True):
        values = {
            'lp_version': '3',
            'need_pts': 1
        }
        if self.group_id:
            values['group_id'] = self.group_id

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
