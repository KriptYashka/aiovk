# aiovk

Асинхронная библиотека для работы с VK (VKontakte) API на Python.

Поддерживает **Bots Long Poll API** (группы) и **User Long Poll API** (пользователи), а также клавиатуры, маршрутизацию событий и систему фильтров.

## Возможности

- Асинхронные запросы через `aiohttp`
- Bots Long Poll (`groups.getLongPollServer`)
- User Long Poll (`messages.getLongPollServer`)
- Система маршрутизации событий с фильтрами (на базе `magic_filter`)
- Построитель клавиатур (обычные и inline)
- Поддержка прокси
- Rate limiting

## Архитектура

```mermaid
graph TB
    subgraph "VK Servers"
        VKAPI[VK API\napi.vk.com]
        LP[Long Poll Server]
    end

    subgraph "aiovk"
        VK[VkApi\nHTTP-клиент с Rate Limit]
        BLP[VkBotLongPoll\nBots Long Poll]
        ULP[VkLongPoll\nUser Long Poll]
        DISP[Dispatcher\nRouter + Event Loop]
    end

    subgraph "Handlers"
        R[Router]
        O[EventObserver]
        H[HandlerObject]
        F[FilterObject]
    end

    VK -->|groups.getLongPollServer| VKAPI
    VK -->|messages.getLongPollServer| VKAPI
    BLP -->|a_check| LP
    ULP -->|a_check| LP
    BLP -->|events| DISP
    ULP -->|events| DISP
    DISP --> R
    R --> O
    O --> H
    H --> F
    F -->|magic_filter| VKBotEvent
```

## Установка

```bash
pip install -r requirements.txt
```

## Быстрый старт (Bots Long Poll)

```python
import asyncio
from core.vk_api import VkApi
from core.bot.bot_longpoll import VkBotLongPoll
from core.handlers.router import Router
from core.bot.bot_events import VkBotMessageEvent

router = Router()


@router.message()
async def echo_handler(event: VkBotMessageEvent):
    await event.answer(f"Вы написали: {event.message.text}")


async def main():
    vk = VkApi(token="your_token")
    server = VkBotLongPoll(vk, group_id=123456)
    await server.update_longpoll_server()

    while True:
        events = await server.get_events()
        for event in events:
            event.vk = vk
            await router.propagate_event(event.type, event)


asyncio.run(main())
```

## Жизненный цикл события

```mermaid
sequenceDiagram
    participant VK as VK Server
    participant LP as Long Poll
    participant Router
    participant Observer
    participant Handler
    participant Filter
    participant CB as Callback

    VK->>LP: groups.getLongPollServer
    LP->>VK: key, server, ts
    loop polling
        LP->>VK: a_check (key, ts, wait)
        VK->>LP: updates[]
        LP->>Router: propagate_event(type, event)
        Router->>Observer: trigger(event)
        loop handlers
            Observer->>Filter: check(event)
            Filter->>Observer: True/False + data
            alt filter passed
                Observer->>Handler: call(event, **data)
                Handler->>CB: callback(event)
                CB->>Handler: response
                Handler->>Observer: HANDLED
            else filter failed
                Observer->>Handler: next handler
            end
        end
        Observer->>Router: HANDLED / UNHANDLED
    end
```

## Структура проекта

```mermaid
classDiagram
    class VkApi {
        +token: str
        +proxy: str
        +v: str
        +method(method, params)
        +send(url, params, wait)
        +close()
    }

    class VkBotLongPoll {
        +vk: VkApi
        +group_id: int
        +wait: int
        +update_longpoll_server()
        +get_events() List~VkBotEvent~
    }

    class VkLongPoll {
        +vk: VkApi
        +wait: int
        +mode: int
        +update_longpoll_server()
        +get_events() List~Event~
    }

    class Router {
        +name: str
        +message: EventObserver
        +callback_query: EventObserver
        +sub_routers: List~Router~
        +include_router(router)
        +propagate_event(type, event)
    }

    class EventObserver {
        +handlers: List~HandlerObject~
        +register(callback, filters)
        +trigger(event) ResponseStatus
    }

    class HandlerObject {
        +callback: CallbackType
        +filters: List~FilterObject~
        +flags: dict
        +check(event) Tuple~bool, dict~
        +call(event)
    }

    class FilterObject {
        +callback: CallbackType
        +magic: MagicFilter
        +call(event) bool~dict~
    }

    class VkBotEvent {
        +raw: dict
        +type: str
        +object: DotDict
        +message: DotDict
        +peer_id: int
        +vk: VkApi
        +answer(text, keyboard)
        +event_answer(text)
    }

    class VkKeyboard {
        +one_time: bool
        +inline: bool
        +add_button(label, color, payload)
        +add_callback_button(label, color, payload)
        +add_line()
        +get_keyboard() str
    }

    VkBotLongPoll --> VkApi
    VkLongPoll --> VkApi
    Router --> EventObserver
    EventObserver --> HandlerObject
    HandlerObject --> FilterObject
    VkBotMessageEvent --|> VkBotEvent
    VkBotCallbackEvent --|> VkBotEvent
```

## События Bots Long Poll

```mermaid
classDiagram
    class VkBotEvent {
        +raw: dict
        +type: str
        +t: str
        +object: DotDict
        +obj: DotDict
        +message: DotDict
        +peer_id: int
        +group_id: int
        +vk: VkApi
        +answer(text, keyboard)
        +event_answer(text)
    }

    class VkBotMessageEvent {
        +from_user: bool
        +from_chat: bool
        +from_group: bool
        +chat_id: int
        +peer_id: int
    }

    class VkBotCallbackEvent {
        +payload: dict
        +message_id: int
    }

    VkBotMessageEvent --|> VkBotEvent
    VkBotCallbackEvent --|> VkBotEvent
```

## Клавиатуры

```mermaid
graph LR
    subgraph "VkKeyboard"
        KB[VkKeyboard]
        KB1[one_time: bool]
        KB2[inline: bool]
        KB3[buttons: List~Line~]
    end

    subgraph "Lines"
        L1[Line 1]
        L2[Line 2]
        L3[Line N]
    end

    subgraph "Buttons"
        BT1[Text]
        BT2[Callback]
        BT3[Location]
        BT4[VKPay]
        BT5[VK Apps]
        BT6[Open Link]
    end

    KB --> L1
    KB --> L2
    KB --> L3
    L1 --> BT1
    L1 --> BT2
    L2 --> BT3
    L2 --> BT4
    L3 --> BT5
    L3 --> BT6
```

Цвета кнопок: `VkKeyboardColor.PRIMARY` (синяя), `SECONDARY` (белая), `NEGATIVE` (красная), `POSITIVE` (зелёная).

## Обработка ошибок

```mermaid
classDiagram
    class VKAPIError {
        +vk_error_code: int
        +vk_error_msg: str
    }

    class VKAuthError {
        +code: 5
    }
    class VKRateLimitError {
        +code: 6
    }
    class VKCaptchaError {
        +code: 14
    }
    class VKAccessDeniedError {
        +code: 15
    }

    VKAuthError --|> VKAPIError
    VKRateLimitError --|> VKAPIError
    VKCaptchaError --|> VKAPIError
    VKAccessDeniedError --|> VKAPIError
    %% ... и ещё 20+ классов ошибок
```

## Примеры

Примеры находятся в папке [`examples/`](examples/):

- `hello_world/` — бот с сообщениями и callback-кнопками
- `keyboard/` — пример клавиатур
- `limits_test/` — тест лимитов

```mermaid
graph LR
    subgraph "examples"
        HW[hello_world]
        KB[keyboard]
        LT[limits_test]
    end

    subgraph "core"
        VK[VkApi]
        BLP[VkBotLongPoll]
        R[Router]
        KEY[VkKeyboard]
    end

    HW --> VK
    HW --> BLP
    HW --> R
    HW --> KEY
    KB --> VK
    KB --> BLP
    KB --> R
    KB --> KEY
```

## Зависимости

- `aiohttp` — асинхронный HTTP-клиент
- `aiohttp_socks` — поддержка прокси
- `certifi` — SSL-сертификаты
- `python-dotenv` — загрузка `.env`
- `magic-filter` — фильтры для обработчиков
