import asyncio
import inspect
import warnings
from dataclasses import dataclass, field
from functools import partial
from typing import Callable, Any

from magic_filter import MagicFilter

from core.handlers.base_filter import Filter

CallbackType = Callable[..., Any]


@dataclass
class CallableObject:
    callback: CallbackType
    awaitable: bool = field(init=False)
    params: set[str] = field(init=False)
    varkw: bool = field(init=False)

    def __post_init__(self) -> None:
        callback = inspect.unwrap(self.callback)
        self.awaitable = inspect.isawaitable(callback) or inspect.iscoroutinefunction(callback)
        spec = inspect.getfullargspec(callback)
        self.params = {*spec.args, *spec.kwonlyargs}
        self.varkw = spec.varkw is not None

    def _prepare_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        if self.varkw:
            return kwargs

        return {k: kwargs[k] for k in self.params if k in kwargs}

    async def call(self, *args: Any, **kwargs: Any) -> Any:
        wrapped = partial(self.callback, *args, **self._prepare_kwargs(kwargs))
        if self.awaitable:
            return await wrapped()
        return await asyncio.to_thread(wrapped)


@dataclass
class FilterObject(CallableObject):
    magic: MagicFilter | None = None

    def __post_init__(self) -> None:
        if isinstance(self.callback, MagicFilter):
            # Экземпляр MagicFilter доступен для вызова, но генерирует
            # только "CallOperation" вместо применения фильтра
            self.magic = self.callback
            self.callback = self.callback.resolve

        super().__post_init__()

        if isinstance(self.callback, Filter):
            self.awaitable = True


@dataclass
class HandlerObject(CallableObject):
    filters: list[FilterObject] | None = None
    flags: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        callback = inspect.unwrap(self.callback)
        if inspect.isclass(callback):
            self.awaitable = True

    async def check(self, *args: Any, **kwargs: Any) -> tuple[bool, dict[str, Any]]:
        if not self.filters:
            return True, kwargs
        for event_filter in self.filters:
            check = await event_filter.call(*args, **kwargs)
            if not check:
                return False, kwargs
            if isinstance(check, dict):
                kwargs.update(check)
        return True, kwargs