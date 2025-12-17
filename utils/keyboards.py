import json
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ButtonAction:
    """Базовый класс для действий кнопок"""
    type: str
    payload: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Преобразует объект в словарь"""
        result = {"type": self.type}
        if self.payload is not None:
            result["payload"] = json.dumps(self.payload)
        return result

    def __dict__(self):
        return self.to_dict()


@dataclass
class TextButtonAction(ButtonAction):
    """Действие для текстовой кнопки"""
    label: str = ""

    def __post_init__(self):
        """Устанавливает тип после инициализации"""
        if not self.type:
            self.type = "text"

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
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

    def to_dict(self) -> dict[str, Any]:
        """Преобразует объект в словарь"""
        result = super().to_dict()
        result["label"] = self.label
        return result


@dataclass
class Button:
    """Класс для представления кнопки"""
    action: ButtonAction
    color: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
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
            inline: Встроенная клавиатура в сообщение
        """
        self._one_time = one_time
        self._inline = inline
        self._buttons: list[list[Button]] = []

    def add_row(self) -> 'Keyboard':
        """
        Добавляет новый ряд кнопок

        Returns:
            self для цепочного вызова
        """
        self._buttons.append([])
        return self

    def add_button(self, button: Button, row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку в указанный ряд

        Args:
            button: Объект кнопки
            row_index: Индекс ряда, по умолчанию последний ряд

        Returns:
            self для цепочного вызова

        Raises:
            IndexError: Если указан неверный индекс ряда
        """
        if row_index is None:
            if not self._buttons:
                self.add_row()
            row_index = -1

        if not (-1 <= row_index <= len(self._buttons) - 1):
            raise IndexError(f"Неверный индекс ряда: {row_index}")

        self._buttons[row_index].append(button)
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

    def add_vkpay_button(self,
                         hash_str: str,
                         payload: Optional[str] = None,
                         row_index: Optional[int] = None) -> 'Keyboard':
        """
        Добавляет кнопку VK Pay

        Args:
            hash_str: Параметры платежа VK Pay
            payload: Дополнительные данные в формате JSON-строки
            row_index: Индекс ряда, по умолчанию последний ряд

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
            row_index: Индекс ряда, по умолчанию последний ряд

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

    def set_buttons(self, buttons=list[list[Button]]):
        self._buttons = buttons

    def get_json(self, indent: Optional[int] = None) -> str:
        """
        Возвращает JSON-представление клавиатуры

        Args:
            indent: Отступ для форматирования JSON. None по умл.

        Returns:
            JSON-строка клавиатуры
        """
        buttons_dict = []
        for row in self._buttons:
            row_dict = [button.to_dict() for button in row]
            buttons_dict.append(row_dict)

        keyboard_dict = {
            "one_time": self._one_time,
            "buttons": buttons_dict
        }

        if self._inline:
            keyboard_dict["inline"] = True

        return json.dumps(keyboard_dict, ensure_ascii=False, indent=indent)

    def get_keyboard(self) -> dict[str, Any]:
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
        self._buttons.clear()
        return self


# Утилитарные функции
def create_payload(data: dict[str, Any]) -> str:
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
