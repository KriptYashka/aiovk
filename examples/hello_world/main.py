import asyncio
import logging

from config import Config

from core.bot.bot_events import VkBotEvent
from core.bot.bot_longpoll import VkBotLongPoll
from core.vk_api import VkApi
from examples.hello_world.dispatcher import dispatcher


async def main():
    logging.basicConfig(level=logging.DEBUG)
    config = Config()
    vk = VkApi(
        config.token,
        config.proxy,
        '5.199',
        is_group_token=True,
    )
    server = VkBotLongPoll(vk)
    await server.update_longpoll_server()
    while True:
        events: list[VkBotEvent] = await server.get_events()
        for event in events:
            event.vk = vk
            await dispatcher.propagate_event(event.type, event)


if __name__ == "__main__":
    asyncio.run(main())
