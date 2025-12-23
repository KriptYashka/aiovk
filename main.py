import asyncio
import logging

from config import Config
from core.longpool import VkLongPoll
from core.vk_api import VkApi


async def main():
    logging.basicConfig(level=logging.DEBUG)
    config = Config()
    vk = VkApi(
        config.token,
        config.proxy,
        '5.199'
    )
    server = VkLongPoll(
        vk,
        group_id=config.group_id
    )
    await server.update_longpoll_server()
    while True:
        events = await server.get_events()
        print(events)


if __name__ == "__main__":
    asyncio.run(main())
