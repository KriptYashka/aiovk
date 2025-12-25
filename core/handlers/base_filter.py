from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any


class Filter(ABC):  # noqa: B024
    if TYPE_CHECKING:
        __call__: Callable[..., Awaitable[bool | dict[str, Any]]]
    else:  # pragma: no cover

        @abstractmethod
        async def __call__(self, *args: Any, **kwargs: Any) -> bool | dict[str, Any]:
            """
            Этот метод должен быть переопределен.

            Принимает входящее событие и должен возвращать значение boolean или dict.

            :return: :class:`bool` or :class:`Dict[str, Any]`
            """

    def update_handler_flags(self, flags: dict[str, Any]) -> None:  # noqa: B027
        """
        Также, если вы хотите расширить флаги обработчика с помощью этого фильтра
        вам следует реализовать этот метод

        :param flags: existing flags, can be updated directly
        """

    def _signature_to_string(self, *args: Any, **kwargs: Any) -> str:
        items = [repr(arg) for arg in args]
        items.extend([f"{k}={v!r}" for k, v in kwargs.items() if v is not None])

        return f"{type(self).__name__}({', '.join(items)})"

    def __await__(self):  # type: ignore # pragma: no cover
        # Необходим только для проверки, и этот метод никогда не вызывается
        return self.__call__