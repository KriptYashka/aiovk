import logging
import sys
import traceback

from typing import Any, Callable, Optional

from core.bot.bot_events import VkBotEvent
from core.handlers.base_filter import Filter
from core.handlers.handler import FilterObject, HandlerObject
from core.handlers.responce import ResponseStatus

CallbackType = Callable[..., Any]  # Повторяется 2 раза в проекте


class EventObserver:
    def __init__(self) -> None:
        self.handlers: list[HandlerObject] = []
        self._handler = HandlerObject(callback=lambda: True, filters=[])

    def filter(self, *filters: CallbackType) -> None:
        """
        Register filter for all handlers of this event observer

        :param filters: positional filters
        """
        if self._handler.filters is None:
            self._handler.filters = []
        self._handler.filters.extend([FilterObject(filter_) for filter_ in filters])

    def register(
            self,
            callback: CallbackType,
            *filters: CallbackType | bool,
            flags: Optional[dict[str, Any]] = None,
            **kwargs: Any,
    ) -> CallbackType:
        """
        Register event handler
        """
        if kwargs:
            raise KeyError(
                "Passing any additional keyword arguments to the registrar method "
                "is not supported.\n"
            )

        if flags is None:
            flags = {}

        for item in filters:
            if isinstance(item, Filter):
                item.update_handler_flags(flags=flags)

        self.handlers.append(
            HandlerObject(
                callback=callback,
                filters=[FilterObject(filter_) for filter_ in filters],
                flags=flags,
            )
        )

        return callback

    def check_root_filters(self, event: VkBotEvent, **kwargs: Any) -> Any:
        return self._handler.check(event, **kwargs)

    async def trigger(self, event: VkBotEvent, *args, **kwargs: Any) -> Optional[int]:
        """
        Передайте событие обработчикам.
        Обработчик будет вызван, когда будут пройдены все его фильтры.
        """
        for handler in self.handlers:
            kwargs["handler"] = handler
            result, data = await handler.check(event, **kwargs)
            if result:
                kwargs.update(data)
                try:
                    await handler.call(event, *args, **kwargs)
                    return ResponseStatus.HANDLED
                except Exception as e:
                    logging.exception("Exception while handling event: %s", e)
                    traceback.print_exc(limit=5)
                    return ResponseStatus.REJECTED

        return ResponseStatus.UNHANDLED

    def __call__(
            self,
            *filters: CallbackType,
            flags: Optional[dict[str, Any]] = None,
            **kwargs: Any,
    ) -> Callable[[CallbackType], CallbackType]:
        """
        Decorator for registering event handlers
        """

        def wrapper(callback: CallbackType) -> CallbackType:
            self.register(callback, *filters, flags=flags, **kwargs)
            return callback

        return wrapper
