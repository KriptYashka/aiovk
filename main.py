import asyncio
import logging

from config import Config

from core.bot_longpool import VkBotLongPoll, VkBotEvent
from core.dispatcher import dispatcher
from core.vk_api import VkApi

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
    await server.update_longpoll_server()
    while True:
        events: list[VkBotEvent] = await server.get_events()
        for event in events:
            event.vk = vk
            await dispatcher.propagate_event(event.type, event)


if __name__ == "__main__":
    asyncio.run(main())
