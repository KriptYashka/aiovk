import asyncio
import datetime

from handlers.message_handler import handle_message
from handlers.callback_handler import handle_callback
from utils.vk_api import VkApi
from utils.events import EventParser, BaseEvent


async def main():
    vk = VkApi()
    await vk.start_longpoll()

    while True:
        updates = await vk.get_updates()
        log = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {len(updates)} | {updates}"
        print(log)
        for update in updates:
            event: BaseEvent = EventParser.parse(update)
            print(event)

if __name__ == "__main__":
    asyncio.run(main())
