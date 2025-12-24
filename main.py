import asyncio
import logging

from config import Config

from core.bot_longpool import VkBotLongPoll
from core.user_longpool import VkLongPoll
from core.vk_api import VkApi

from routers.main_router import router as main_router


async def main():
    logging.basicConfig(level=logging.DEBUG)
    config = Config()
    vk = VkApi(
        config.token,
        config.proxy,
        '5.199'
    )
    server = VkBotLongPoll(
        vk,
        group_id=config.group_id
    )
    # event_handler = EventHandler()
    await server.update_longpoll_server()
    while True:
        events = await server.get_events()
        for event in events:
            await main_router.propagate_event(event.type.value, event)
        # await event_handler.handle(events)


if __name__ == "__main__":
    asyncio.run(main())
