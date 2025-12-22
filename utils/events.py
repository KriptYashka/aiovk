"""
Документация VK событий: https://dev.vk.com/ru/api/user-long-poll/getting-started#Дополнительные%20поля%20сообщений
"""

import time
from dataclasses import dataclass
from typing import Any


class MessageFlags:
    """
    Флаги сообщений. Некоторые могут быть устаревшими.
    """
    UNREAD = 1
    OUTBOX = 2
    REPLIED = 4
    IMPORTANT = 8
    CHAT = 16  # Устаревший
    FRIENDS = 32
    SPAM = 64
    DELETED = 128
    FIXED = 256  # Устаревший
    MEDIA = 512  # Устаревший
    HIDDEN = 65536
    DELETE_FOR_ALL = 64  # Для версий >= 3
    NOT_DELIVERED = 64  # Для входящих сообщений с TTL


@dataclass
class BaseEvent:
    """Базовое событие"""
    code: int
    description: str

    @classmethod
    def from_list(cls, data: list[Any]) -> 'BaseEvent':
        """Создает событие из списка"""
        raise NotImplementedError

    def __str__(self):
        return self.description


@dataclass
class MessageFlagsEvent(BaseEvent):
    """
    События с флагами
    """
    message_id: int
    flags_or_mask: int
    extra_fields: list[Any]

    @classmethod
    def from_list(cls, data: list[Any]) -> 'MessageFlagsEvent':
        if cls.code is None:
            raise AttributeError("Event code in dataclass is not specified")
        return cls(
            code=cls.code,
            description=cls.description,
            message_id=data[0],
            flags_or_mask=data[1],
            extra_fields=data[2:]
        )


@dataclass
class MessageFlagsReplaceEvent(MessageFlagsEvent):
    code = 1
    description = "Замена флагов сообщения (FLAGS:=flags)"


@dataclass
class MessageFlagsSetEvent(MessageFlagsEvent):
    code = 2
    description = "Установка флагов сообщения (FLAGS:=flags)"


@dataclass
class MessageFlagsResetEvent(MessageFlagsEvent):
    code = 3
    description = "Сброс флагов сообщения (FLAGS&=~mask)"


@dataclass
class NewMessageEvent(BaseEvent):
    """
    По документации поля другие.
    """
    code = 4
    description = "Добавление нового сообщения"

    message_id: int
    flags: int
    peer_id: int
    extra_fields: list[Any]

    @classmethod
    def from_list(cls, data: list[Any]) -> 'NewMessageEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            message_id=data[0],
            flags=data[1],
            peer_id=data[2],
            extra_fields=data[3:]
        )


@dataclass
class MessageEditEvent(BaseEvent):
    code = 5
    description = "Редактирование сообщения"

    message_id: int
    mask: int
    peer_id: int
    timestamp: int
    new_text: str
    attachments: list[Any]

    @classmethod
    def from_list(cls, data: list[Any]) -> 'MessageEditEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            message_id=data[0],
            mask=data[1],
            peer_id=data[2],
            timestamp=data[3],
            new_text=data[4],
            attachments=data[5]
        )


@dataclass
class IncomingMessagesReadEvent(BaseEvent):
    code = 6
    description = "Прочтение всех входящих сообщений"

    peer_id: int
    local_id: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'IncomingMessagesReadEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            peer_id=data[0],
            local_id=data[1]
        )


@dataclass
class OutgoingMessagesReadEvent(BaseEvent):
    code = 7
    description = "Прочтение всех исходящих сообщений"

    peer_id: int
    local_id: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'OutgoingMessagesReadEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            peer_id=data[0],
            local_id=data[1]
        )


@dataclass
class UserOnlineEvent(BaseEvent):
    code = 8
    description = "Пользователь стал онлайн"
    user_id: int
    extra: int
    timestamp: int

    @property
    def platform_id(self) -> int:
        """Идентификатор платформы из младшего байта extra"""
        return self.extra % 256

    @property
    def is_online(self) -> bool:
        """Пользователь онлайн (extra != 0)"""
        return self.extra != 0

    @classmethod
    def from_list(cls, data: list[Any]) -> 'UserOnlineEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            user_id=abs(data[0]),  # Убираем минус
            extra=data[1],
            timestamp=data[2]
        )


@dataclass
class UserOfflineEvent(BaseEvent):
    code = 9
    description = "Пользователь стал оффлайн"

    user_id: int
    flags: int
    timestamp: int

    @property
    def is_timeout(self) -> bool:
        """Оффлайн по таймауту (flags == 1)"""
        return self.flags == 1

    @property
    def left_site(self) -> bool:
        """Пользователь покинул сайт (flags == 0)"""
        return self.flags == 0

    @classmethod
    def from_list(cls, data: list[Any]) -> 'UserOfflineEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            user_id=abs(data[0]),  # Убираем минус
            flags=data[1],
            timestamp=data[2]
        )


@dataclass
class PeerFlagsEvent(BaseEvent):
    peer_id: int
    flag_or_mask: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'PeerFlagsEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            peer_id=data[0],
            flag_or_mask=data[1]
        )


@dataclass
class PeerFlagsResetEvent(PeerFlagsEvent):
    code = 10
    description = "Сброс флагов диалога (PEER_FLAGS &= ~flags)"


@dataclass
class PeerFlagsReplaceEvent(PeerFlagsEvent):
    code = 11
    description = "Замена флагов диалога (PEER_FLAGS:=flags)"


@dataclass
class PeerFlagsSetEvent(PeerFlagsEvent):
    code = 12
    description = "Установка флагов диалога (PEER_FLAGS|=flags)"


@dataclass
class ActionIdEvent(BaseEvent):
    peer_id: int
    obj_id: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'ActionIdEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            peer_id=data[0],
            obj_id=data[1],
        )


@dataclass
class MessagesDeleteEvent(ActionIdEvent):
    code = 13
    description = "Удаление всех сообщений в диалоге"


@dataclass
class MessagesRestoreEvent(ActionIdEvent):
    code = 14
    description = "Восстановление недавно удаленных сообщений"


@dataclass
class MajorIdChangeEvent(ActionIdEvent):
    code = 20
    description = "Изменился major_id в диалоге"


@dataclass
class MinorIdChangeEvent(ActionIdEvent):
    code = 21
    description = "Изменился minor_id в диалоге"


@dataclass
class ChatParamsChangeEvent(ActionIdEvent):
    code = 51
    description = "Изменение параметров беседы"

    @property
    def is_self(self) -> bool:
        """Изменения вызваны самим пользователем"""
        return self.obj_id == 1


@dataclass
class ChatInfoChangeEvent(BaseEvent):
    code = 52
    description = "Изменение информации чата"
    type_id: int
    peer_id: int
    info: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'ChatInfoChangeEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            type_id=data[0],
            peer_id=data[1],
            info=data[2],
        )


@dataclass
class UserTypingEvent(BaseEvent):
    code = 61
    description = "Пользователь набирает текст в диалоге"

    user_id: int
    flags: int

    @property
    def is_typing(self) -> bool:
        """Пользователь набирает текст"""
        return self.flags == 1

    @classmethod
    def from_list(cls, data: list[Any]) -> 'UserTypingEvent':
        return cls(
            code=61,
            description="Пользователь набирает текст в диалоге",
            user_id=data[0],
            flags=data[1]
        )


@dataclass
class UserTypingInChatEvent(BaseEvent):
    code = 62
    description = "Пользователь набирает текст в беседе"

    user_id: int
    chat_id: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'UserTypingInChatEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            user_id=data[0],
            chat_id=data[1]
        )


@dataclass
class UsersTypingEvent(BaseEvent):
    code = 63
    description = "Пользователи набирают текст в беседе"

    user_ids: list[int]
    peer_id: int
    total_count: int
    ts: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'UsersTypingEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            user_ids=data[0],
            peer_id=data[1],
            total_count=data[2],
            ts=data[3]
        )


@dataclass
class UsersRecordingAudioEvent(BaseEvent):
    code = 64
    description = "Пользователи записывают аудиосообщение в беседе"

    user_ids: list[int]
    peer_id: int
    total_count: int
    ts: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'UsersRecordingAudioEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            user_ids=data[0],
            peer_id=data[1],
            total_count=data[2],
            ts=data[3]
        )


@dataclass
class CallEvent(BaseEvent):
    code = 70
    description = "Пользователь совершил звонок"

    user_id: int
    call_id: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'CallEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            user_id=data[0],
            call_id=data[1]
        )


@dataclass
class CounterUpdateEvent(BaseEvent):
    code = 80
    description = "Счетчик в левом меню обновлен"

    count: int

    @classmethod
    def from_list(cls, data: list[Any]) -> 'CounterUpdateEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            count=data[0]
        )


@dataclass
class NotificationSettingsChangeEvent(BaseEvent):
    code = 114
    description = "Изменились настройки оповещений"
    peer_id: int
    sound: int
    disabled_until: int

    @property
    def sound_enabled(self) -> bool:
        """Звуковые оповещения включены"""
        return self.sound == 1

    @property
    def notifications_forever_disabled(self) -> bool:
        """Оповещения выключены навсегда"""
        return self.disabled_until == -1

    @property
    def notifications_enabled(self) -> bool:
        """Оповещения включены"""
        return self.disabled_until == 0

    @classmethod
    def from_list(cls, data: list[Any]) -> 'NotificationSettingsChangeEvent':
        return cls(
            code=cls.code,
            description=cls.description,
            peer_id=data[0],
            sound=data[1],
            disabled_until=data[2]
        )


class EventParser:
    """Парсер событий из списка"""
    EVENT_CLASSES = {
        1: MessageFlagsReplaceEvent,
        2: MessageFlagsSetEvent,
        3: MessageFlagsResetEvent,
        4: NewMessageEvent,
        5: MessageEditEvent,
        6: IncomingMessagesReadEvent,
        7: OutgoingMessagesReadEvent,
        8: UserOnlineEvent,
        9: UserOfflineEvent,
        10: PeerFlagsResetEvent,
        11: PeerFlagsReplaceEvent,
        12: PeerFlagsSetEvent,
        13: MessagesDeleteEvent,
        14: MessagesRestoreEvent,
        20: MajorIdChangeEvent,
        21: MinorIdChangeEvent,
        51: ChatParamsChangeEvent,
        52: ChatInfoChangeEvent,
        61: UserTypingEvent,
        62: UserTypingInChatEvent,
        63: UsersTypingEvent,
        64: UsersRecordingAudioEvent,
        70: CallEvent,
        80: CounterUpdateEvent,
        114: NotificationSettingsChangeEvent,
    }

    @classmethod
    def parse(cls, data: list[Any]) -> BaseEvent:
        """
        Парсит событие из списка

        Args:
            data: Список данных события

        Returns:
            BaseEvent: Объект события соответствующего типа. Если тип не найден - BaseEvent

        Raises:
            ValueError: Если список события пустой
        """
        if not data:
            raise ValueError("Update list is empty")

        event_code = data[0]

        if event_code not in cls.EVENT_CLASSES:
            return BaseEvent(  # Создаем базовое событие для неподдерживаемых кодов
                code=event_code,
                description=f"Неизвестное событие (код: {event_code})"
            )

        event_class = cls.EVENT_CLASSES[event_code]
        return event_class.from_list(data[1:])


def main():
    # Пример 1: Пользователь онлайн
    online_data = [8, -123456, 129, int(time.time())]
    event1 = EventParser.parse(online_data)
    print(f"Событие {event1.code}: {event1.description}")
    if isinstance(event1, UserOnlineEvent):
        print(f"Пользователь {event1.user_id} онлайн, платформа: {event1.platform_id}")

    # Пример 2: Новое сообщение
    message_data = [4, 987654, 32, 555, "extra_field1", "extra_field2"]
    event2 = EventParser.parse(message_data)
    print(f"\nСобытие {event2.code}: {event2.description}")
    if isinstance(event2, NewMessageEvent):
        print(f"Новое сообщение ID: {event2.message_id}, флаги: {event2.flags}")

    # Пример 3: Пользователь печатает
    typing_data = [61, 123456, 1]
    event3 = EventParser.parse(typing_data)
    print(f"\nСобытие {event3.code}: {event3.description}")
    if isinstance(event3, UserTypingEvent):
        print(f"Пользователь {event3.user_id} печатает: {event3.is_typing}")

    # Пример 4: Неизвестное событие
    unknown_data = [999, "unknown", "data"]
    event4 = EventParser.parse(unknown_data)
    print(f"\nСобытие {event4.code}: {event4.description}")


if __name__ == "__main__":
    main()
