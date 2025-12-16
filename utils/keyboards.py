import json
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field, asdict


@dataclass
class ButtonAction:
    """Базовый класс для действий кнопок"""
    type: str
    payload: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = {"type": self.type}
        if self.payload is not None:
            result["payload"] = self.payload
        return result


@dataclass
class TextButtonAction(ButtonAction):
    """Действие для текстовой кнопки"""
    label: str = ""

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "text"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = super().to_dict()
        result["label"] = self.label
        return result


@dataclass
class LocationButtonAction(ButtonAction):
    """Действие для кнопки локации"""

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "location"


@dataclass
class VKPayButtonAction(ButtonAction):
    """Действие для кнопки VK Pay"""
    hash: str = ""

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "vkpay"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = super().to_dict()
        result["hash"] = self.hash
        return result


@dataclass
class OpenLinkButtonAction(ButtonAction):
    """Действие для кнопки открытия ссылки"""
    link: str = ""
    label: str = ""

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "open_link"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = super().to_dict()
        result.update({
            "link": self.link,
            "label": self.label
        })
        return result


@dataclass
class OpenAppButtonAction(ButtonAction):
    """Действие для кнопки открытия приложения"""
    app_id: int = 0
    label: str = ""
    owner_id: Optional[int] = None
    hash: Optional[str] = None

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "open_app"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = super().to_dict()
        result.update({
            "app_id": self.app_id,
            "label": self.label
        })
        if self.owner_id is not None:
            result["owner_id"] = self.owner_id
        if self.hash is not None:
            result["hash"] = self.hash
        return result


@dataclass
class CallbackButtonAction(ButtonAction):
    """Действие для callback-кнопки"""
    label: str = ""

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "callback"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = super().to_dict()
        result["label"] = self.label
        return result


@dataclass
class Button:
    """Класс для представления кнопки"""
    action: ButtonAction
    color: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        result = {"action": self.action.to_dict()}
        if self.color is not None:
            result["color"] = self.color
        return result


class ButtonColor:
    """Константы цветов кнопок"""
    PRIMARY = "primary"  # Основное действие
    SECONDARY = "secondary"  # Обычные кнопки
    NEGATIVE = "negative"  # Опасное действие или отмена
    POSITIVE = "positive"  # Согласие или подтверждение


class Keyboard:
    """Класс для создания клавиатуры VK"""

    def __init__(self, one_time: bool = False, inline: bool = False):
        """
        Инициализация клавиатуры

        Args:
            one_time: Скрывать клавиатуру после нажатия
            inline: Инлайн клавиатура
        """
        self.one_time = one_time
        self.inline = inline
        self.buttons: List[List[Button]] = []

    def add_row(self) -> 'Keyboard':
        """
        Добавляет новый ряд кнопок

        Returns:
            self для цепочного вызова
        """
        self.buttons.append([])
        return self

    def add_button(self, button: Button, row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку в указанный ряд

        Args:
            button: Объект кнопки
            row_index: Индекс ряда (последний, если не указан)

        Returns:
            self для цепочного вызова

        Raises:
            IndexError: Если указан неверный индекс ряда
        """
        if row_index is None:
            if not self.buttons:
                self.add_row()
            row_index = -1

        if row_index < 0 or row_index >= len(self.buttons):
            raise IndexError(f"Неверный индекс ряда: {row_index}")

        self.buttons[row_index].append(button)
        return self

    def add_text_button(self,
                        label: str,
                        color: Optional[str] = None,
                        payload: Optional[str] = None,
                        row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет текстовую кнопку

        Args:
            label: Текст кнопки (макс. 40 символов)
            color: Цвет кнопки
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда

        Returns:
            self для цепочного вызова

        Raises:
            ValueError: Если payload превышает 255 символов
        """
        if len(label) > 40:
            raise ValueError("Текст кнопки не должен превышать 40 символов")

        if payload is not None and len(payload) > 255:
            raise ValueError("Payload не должен превышать 255 символов")

        action = TextButtonAction(type="text", label=label, payload=payload)
        button = Button(action=action, color=color)

        return self.add_button(button, row_index)

    def add_location_button(self,
                            payload: Optional[str] = None,
                            row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку локации

        Args:
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда

        Returns:
            self для цепочного вызова

        Raises:
            ValueError: Если payload превышает 255 символов
        """
        if payload is not None and len(payload) > 255:
            raise ValueError("Payload не должен превышать 255 символов")

        action = LocationButtonAction(type="location", payload=payload)
        button = Button(action=action)

        return self.add_button(button, row_index)

    def add_vkpay_button(self,
                         hash_str: str,
                         payload: Optional[str] = None,
                         row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку VK Pay

        Args:
            hash_str: Параметры платежа VK Pay
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда

        Returns:
            self для цепочного вызова

        Raises:
            ValueError: Если payload превышает 255 символов
        """
        if payload is not None and len(payload) > 255:
            raise ValueError("Payload не должен превышать 255 символов")

        action = VKPayButtonAction(type="vkpay", hash=hash_str, payload=payload)
        button = Button(action=action)

        return self.add_button(button, row_index)

    def add_open_link_button(self,
                             link: str,
                             label: str,
                             payload: Optional[str] = None,
                             row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку открытия ссылки

        Args:
            link: Ссылка для открытия
            label: Текст кнопки
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда

        Returns:
            self для цепочного вызова

        Raises:
            ValueError: Если текст кнопки превышает 40 символов
            ValueError: Если payload превышает 255 символов
        """
        if len(label) > 40:
            raise ValueError("Текст кнопки не должен превышать 40 символов")

        if payload is not None and len(payload) > 255:
            raise ValueError("Payload не должен превышать 255 символов")

        action = OpenLinkButtonAction(type="open_link", link=link, label=label, payload=payload)
        button = Button(action=action)

        return self.add_button(button, row_index)

    def add_open_app_button(self,
                            app_id: int,
                            label: str,
                            owner_id: Optional[int] = None,
                            hash_str: Optional[str] = None,
                            payload: Optional[str] = None,
                            row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку открытия приложения

        Args:
            app_id: ID приложения
            label: Текст кнопки
            owner_id: ID сообщества
            hash_str: Хеш для навигации
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда

        Returns:
            self для цепочного вызова

        Raises:
            ValueError: Если текст кнопки превышает 40 символов
            ValueError: Если payload превышает 255 символов
        """
        if len(label) > 40:
            raise ValueError("Текст кнопки не должен превышать 40 символов")

        if payload is not None and len(payload) > 255:
            raise ValueError("Payload не должен превышать 255 символов")

        action = OpenAppButtonAction(
            type="open_app",
            app_id=app_id,
            label=label,
            owner_id=owner_id,
            hash=hash_str,
            payload=payload
        )
        button = Button(action=action)

        return self.add_button(button, row_index)

    def add_callback_button(self,
                            label: str,
                            color: Optional[str] = None,
                            payload: Optional[str] = None,
                            row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет callback-кнопку

        Args:
            label: Текст кнопки (макс. 40 символов)
            color: Цвет кнопки
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда

        Returns:
            self для цепочного вызова

        Raises:
            ValueError: Если текст кнопки превышает 40 символов
            ValueError: Если payload превышает 255 символов
        """
        if len(label) > 40:
            raise ValueError("Текст кнопки не должен превышать 40 символов")

        if payload is not None and len(payload) > 255:
            raise ValueError("Payload не должен превышать 255 символов")

        action = CallbackButtonAction(type="callback", label=label, payload=payload)
        button = Button(action=action, color=color)

        return self.add_button(button, row_index)

    def get_json(self, indent: Optional[int] = None) -> str:
        """
        Возвращает JSON-представление клавиатуры

        Args:
            indent: Отступ для форматирования JSON

        Returns:
            JSON-строка клавиатуры
        """
        # Преобразуем кнопки в словари
        buttons_dict = []
        for row in self.buttons:
            row_dict = [button.to_dict() for button in row]
            buttons_dict.append(row_dict)

        # Создаем словарь клавиатуры
        keyboard_dict = {
            "one_time": self.one_time,
            "buttons": buttons_dict
        }

        # Добавляем поле inline если оно True
        if self.inline:
            keyboard_dict["inline"] = True

        return json.dumps(keyboard_dict, ensure_ascii=False, indent=indent)

    def get_keyboard(self) -> Dict[str, Any]:
        """
        Возвращает словарь клавиатуры (для API)

        Returns:
            Словарь клавиатуры
        """
        return json.loads(self.get_json())

    def clear(self) -> 'Keyboard':
        """
        Очищает клавиатуру

        Returns:
            self для цепочного вызова
        """
        self.buttons.clear()
        return self

    @classmethod
    def create_empty(cls) -> 'Keyboard':
        """
        Создает пустую клавиатуру

        Returns:
            Новая пустая клавиатура
        """
        return cls()

    @classmethod
    def create_one_time(cls) -> 'Keyboard':
        """
        Создает одноразовую клавиатуру

        Returns:
            Новая одноразовая клавиатура
        """
        return cls(one_time=True)

    @classmethod
    def create_inline(cls) -> 'Keyboard':
        """
        Создает инлайн клавиатуру

        Returns:
            Новая инлайн клавиатура
        """
        return cls(inline=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Keyboard':
        """
        Создает клавиатуру из словаря

        Args:
            data: Словарь с данными клавиатуры

        Returns:
            Новая клавиатура

        Raises:
            ValueError: Если данные невалидны
        """
        one_time = data.get("one_time", False)
        inline = data.get("inline", False)

        keyboard = cls(one_time=one_time, inline=inline)

        if "buttons" in data:
            for row in data["buttons"]:
                keyboard.add_row()
                for button_data in row:
                    action_data = button_data.get("action", {})
                    color = button_data.get("color")

                    action_type = action_data.get("type")
                    payload = action_data.get("payload")

                    if action_type == "text":
                        label = action_data.get("label", "")
                        keyboard.add_text_button(label, color, payload)
                    elif action_type == "location":
                        keyboard.add_location_button(payload)
                    elif action_type == "vkpay":
                        hash_str = action_data.get("hash", "")
                        keyboard.add_vkpay_button(hash_str, payload)
                    elif action_type == "open_link":
                        link = action_data.get("link", "")
                        label = action_data.get("label", "")
                        keyboard.add_open_link_button(link, label, payload)
                    elif action_type == "open_app":
                        app_id = action_data.get("app_id", 0)
                        label = action_data.get("label", "")
                        owner_id = action_data.get("owner_id")
                        hash_str = action_data.get("hash")
                        keyboard.add_open_app_button(app_id, label, owner_id, hash_str, payload)
                    elif action_type == "callback":
                        label = action_data.get("label", "")
                        keyboard.add_callback_button(label, color, payload)

        return keyboard


# Утилитарные функции
def create_payload(data: Dict[str, Any]) -> str:
    """
    Создает JSON-строку payload из словаря

    Args:
        data: Словарь с данными

    Returns:
        JSON-строка

    Raises:
        ValueError: Если результат превышает 255 символов
    """
    payload_str = json.dumps(data, ensure_ascii=False)
    if len(payload_str) > 255:
        raise ValueError("Payload не должен превышать 255 символов")
    return payload_str


def validate_payload(payload: str) -> bool:
    """
    Проверяет валидность payload

    Args:
        payload: JSON-строка для проверки

    Returns:
        True если payload валиден

    Raises:
        ValueError: Если payload не является валидным JSON
        ValueError: Если payload превышает 255 символов
    """
    if len(payload) > 255:
        raise ValueError("Payload не должен превышать 255 символов")

    try:
        json.loads(payload)
        return True
    except json.JSONDecodeError as e:
        raise ValueError(f"Невалидный JSON в payload: {e}")

    return True


# Примеры использования
if __name__ == "__main__":
    print("=" * 50)
    print("КОНСТРУКТОР КЛАВИАТУР VK - ИСПРАВЛЕННАЯ ВЕРСИЯ")
    print("=" * 50)

    # Пример 1: Простая клавиатура с текстовыми кнопками
    print("\nПример 1: Простая клавиатура с текстовыми кнопками")
    keyboard1 = Keyboard(one_time=True)

    # Используем правильный payload - JSON-строка
    keyboard1.add_text_button(
        "Красный",
        ButtonColor.NEGATIVE,
        '{"button": "red", "action": "select_color"}'
    ).add_text_button(
        "Зеленый",
        ButtonColor.POSITIVE,
        '{"button": "green", "action": "select_color"}'
    ).add_row().add_text_button(
        "Синий",
        ButtonColor.PRIMARY,
        '{"button": "blue", "action": "select_color"}'
    ).add_text_button(
        "Белый",
        ButtonColor.SECONDARY,
        '{"button": "white", "action": "select_color"}'
    )

    print(keyboard1.get_json(indent=2))
    print("\n" + "=" * 50)

    # Пример 2: Клавиатура с разными типами кнопок
    print("\nПример 2: Клавиатура с разными типами кнопок")
    keyboard2 = Keyboard()

    # Первый ряд: кнопка локации
    keyboard2.add_location_button('{"action": "send_location"}')

    # Второй ряд: кнопка VK Pay
    keyboard2.add_row().add_vkpay_button(
        "action=transfer-to-group&group_id=12345&aid=10",
        '{"action": "vkpay_transfer"}'
    )

    # Третий ряд: текст и callback кнопки
    keyboard2.add_row()
    keyboard2.add_text_button(
        "Текстовая кнопка",
        ButtonColor.PRIMARY,
        '{"type": "text", "action": "send_text"}'
    )
    keyboard2.add_callback_button(
        "Callback",
        ButtonColor.SECONDARY,
        '{"type": "callback", "action": "callback_action"}'
    )

    # Четвертый ряд: открытие ссылки и приложения
    keyboard2.add_row()
    keyboard2.add_open_link_button(
        "https://vk.com",
        "Открыть VK",
        '{"link": "vk", "action": "open_external"}'
    )
    keyboard2.add_open_app_button(
        123456,
        "Открыть приложение",
        payload='{"app": "test_app", "action": "open_app"}'
    )

    print(keyboard2.get_json(indent=2))
    print("\n" + "=" * 50)

    # Пример 3: Использование утилитной функции create_payload
    print("\nПример 3: Использование утилитной функции create_payload")
    keyboard3 = Keyboard.create_inline()

    payload1 = create_payload({"action": "vote", "vote": "like", "user_id": 12345})
    payload2 = create_payload({"action": "vote", "vote": "dislike", "user_id": 12345})
    payload3 = create_payload({"action": "show_results", "poll_id": "abc123"})

    keyboard3.add_text_button("👍", ButtonColor.POSITIVE, payload1) \
        .add_text_button("👎", ButtonColor.NEGATIVE, payload2) \
        .add_row() \
        .add_callback_button("Результаты", ButtonColor.PRIMARY, payload3)

    print(keyboard3.get_json(indent=2))
    print("\n" + "=" * 50)

    # Пример 4: Восстановление клавиатуры из словаря
    print("\nПример 4: Восстановление клавиатуры из словаря")

    keyboard_dict = {
        "one_time": True,
        "buttons": [
            [
                {
                    "action": {
                        "type": "text",
                        "label": "Да",
                        "payload": '{"answer": "yes"}'
                    },
                    "color": "positive"
                },
                {
                    "action": {
                        "type": "text",
                        "label": "Нет",
                        "payload": '{"answer": "no"}'
                    },
                    "color": "negative"
                }
            ]
        ]
    }

    restored_keyboard = Keyboard.from_dict(keyboard_dict)
    print("Восстановленная клавиатура:")
    print(restored_keyboard.get_json(indent=2))
    print("\n" + "=" * 50)

    # Пример 5: Проверка валидности payload
    print("\nПример 5: Проверка валидности payload")

    try:
        valid_payload = '{"action": "test", "data": "valid"}'
        is_valid = validate_payload(valid_payload)
        print(f"Payload '{valid_payload}' валиден: {is_valid}")

        invalid_json = '{"action": "test", "data": invalid}'
        is_valid = validate_payload(invalid_json)
        print(f"Payload '{invalid_json}' валиден: {is_valid}")
    except ValueError as e:
        print(f"Ошибка валидации: {e}")

    try:
        too_long_payload = '{"data": "' + "x" * 250 + '"}'
        is_valid = validate_payload(too_long_payload)
        print(f"Payload длиной {len(too_long_payload)} валиден: {is_valid}")
    except ValueError as e:
        print(f"Ошибка валидации (длина): {e}")

    print("\n" + "=" * 50)

    # Пример 6: Полная клавиатура для бота поддержки
    print("\nПример 6: Полная клавиатура для бота поддержки")

    support_keyboard = Keyboard(one_time=False)

    # Основные команды
    support_keyboard.add_text_button(
        "📋 Список команд",
        ButtonColor.PRIMARY,
        create_payload({"command": "help"})
    ).add_text_button(
        "❓ Задать вопрос",
        ButtonColor.SECONDARY,
        create_payload({"command": "ask_question"})
    )

    # Дополнительные функции
    support_keyboard.add_row()
    support_keyboard.add_text_button(
        "📞 Связаться с поддержкой",
        ButtonColor.POSITIVE,
        create_payload({"command": "contact_support"})
    ).add_text_button(
        "⭐ Оценить бота",
        ButtonColor.SECONDARY,
        create_payload({"command": "rate_bot"})
    )

    # Настройки
    support_keyboard.add_row()
    support_keyboard.add_text_button(
        "⚙️ Настройки уведомлений",
        ButtonColor.PRIMARY,
        create_payload({"command": "notification_settings"})
    ).add_text_button(
        "👤 Мой профиль",
        ButtonColor.SECONDARY,
        create_payload({"command": "my_profile"})
    )

    print(support_keyboard.get_json(indent=2))

    # Получение словаря для API
    keyboard_api_data = support_keyboard.get_keyboard()
    print(f"\nДанные для API (тип: {'инлайн' if support_keyboard.inline else 'обычная'}):")
    print(f"Количество рядов: {len(support_keyboard.buttons)}")
    total_buttons = sum(len(row) for row in support_keyboard.buttons)
    print(f"Всего кнопок: {total_buttons}")