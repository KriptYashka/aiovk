# -*- coding: utf-8 -*-
"""
:authors: deker104, python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""
import logging
from enum import Enum
from typing import Optional

import aiohttp
from aiohttp.web_exceptions import HTTPError

from core.keyboards import VkKeyboard
from core.vk_api import VkApi

CHAT_START_ID = int(2E9)

class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class VkBotEventType(Enum):
    MESSAGE_NEW = 'message_new'
    MESSAGE_REPLY = 'message_reply'
    MESSAGE_EDIT = 'message_edit'
    MESSAGE_EVENT = 'message_event'

    MESSAGE_TYPING_STATE = 'message_typing_state'

    MESSAGE_ALLOW = 'message_allow'

    MESSAGE_DENY = 'message_deny'

    PHOTO_NEW = 'photo_new'

    PHOTO_COMMENT_NEW = 'photo_comment_new'
    PHOTO_COMMENT_EDIT = 'photo_comment_edit'
    PHOTO_COMMENT_RESTORE = 'photo_comment_restore'

    PHOTO_COMMENT_DELETE = 'photo_comment_delete'

    AUDIO_NEW = 'audio_new'

    VIDEO_NEW = 'video_new'

    VIDEO_COMMENT_NEW = 'video_comment_new'
    VIDEO_COMMENT_EDIT = 'video_comment_edit'
    VIDEO_COMMENT_RESTORE = 'video_comment_restore'

    VIDEO_COMMENT_DELETE = 'video_comment_delete'

    WALL_POST_NEW = 'wall_post_new'
    WALL_REPOST = 'wall_repost'

    WALL_REPLY_NEW = 'wall_reply_new'
    WALL_REPLY_EDIT = 'wall_reply_edit'
    WALL_REPLY_RESTORE = 'wall_reply_restore'

    WALL_REPLY_DELETE = 'wall_reply_delete'

    BOARD_POST_NEW = 'board_post_new'
    BOARD_POST_EDIT = 'board_post_edit'
    BOARD_POST_RESTORE = 'board_post_restore'

    BOARD_POST_DELETE = 'board_post_delete'

    MARKET_COMMENT_NEW = 'market_comment_new'
    MARKET_COMMENT_EDIT = 'market_comment_edit'
    MARKET_COMMENT_RESTORE = 'market_comment_restore'

    MARKET_COMMENT_DELETE = 'market_comment_delete'

    GROUP_LEAVE = 'group_leave'

    GROUP_JOIN = 'group_join'

    USER_BLOCK = 'user_block'

    USER_UNBLOCK = 'user_unblock'

    POLL_VOTE_NEW = 'poll_vote_new'

    GROUP_OFFICERS_EDIT = 'group_officers_edit'

    GROUP_CHANGE_SETTINGS = 'group_change_settings'

    GROUP_CHANGE_PHOTO = 'group_change_photo'

    VKPAY_TRANSACTION = 'vkpay_transaction'


class VkBotEvent(object):
    """ Событие Bots Long Poll

    :ivar raw: событие, в каком виде было получено от сервера

    :ivar type: тип события
    :vartype type: VkBotEventType or str

    :ivar t: сокращение для type
    :vartype t: VkBotEventType or str

    :ivar object: объект события, в каком виде был получен от сервера
    :ivar obj: сокращение для object

    :ivar group_id: ID группы бота
    :vartype group_id: int
    """

    __slots__ = (
        'raw',
        't', 'type',
        'obj', 'object',
        'client_info', 'message',
        'group_id', 'vk'
    )

    def __init__(self, raw):
        self.raw = raw
        self.vk: Optional[VkApi] = None  # Поле для VK API

        try:
            self.type = VkBotEventType(raw['type']).value
        except ValueError:
            self.type = raw['type']

        self.t = self.type  # shortcut

        self.object = DotDict(raw['object'])
        try:
            self.message = DotDict(raw['object']['message'])
        except KeyError:
            self.message = None
        self.obj = self.object
        try:
            self.client_info = DotDict(raw['object']['client_info'])
        except KeyError:
            self.client_info = None

        self.group_id = raw['group_id']

    def __repr__(self):
        return f'<{type(self)}({self.raw})>'


class VkBotMessageEvent(VkBotEvent):
    """ Событие с сообщением Bots Long Poll

    :ivar from_user: сообщение от пользователя
    :vartype from_user: bool

    :ivar from_chat: сообщение из беседы
    :vartype from_chat: bool

    :ivar from_group: сообщение от группы
    :vartype from_group: bool

    :ivar chat_id: ID чата
    :vartype chat_id: int
    """

    __slots__ = ('from_user', 'from_chat', 'from_group', 'chat_id', 'peer_id')

    def __init__(self, raw):
        super(VkBotMessageEvent, self).__init__(raw)

        self.from_user = False
        self.from_chat = False
        self.from_group = False
        self.chat_id = None

        self.peer_id = self.obj.peer_id or self.message.peer_id

        if self.peer_id < 0:
            self.from_group = True
        elif self.peer_id < CHAT_START_ID:
            self.from_user = True
        else:
            self.from_chat = True
            self.chat_id = self.peer_id - CHAT_START_ID

    async def answer(self, text: str, keyboard: VkKeyboard = None):
        params = {
            "group_id": self.group_id,
            "peer_id": self.peer_id,
            "message": text,
            "random_id": 0,
        }
        await self.vk.method("messages.send", params)

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
