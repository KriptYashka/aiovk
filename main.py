import asyncio
import datetime

from handlers.message_handler import handle_message
from handlers.callback_handler import handle_callback
from keyboards.main_keyboard import create_main_keyboard
from utils.vk_api import VkApi
from utils.events import EventParser, BaseEvent, NewMessageEvent


async def main():
    vk = VkApi()
    await vk.start_longpoll()

    while True:
        updates = await vk.get_updates()
        log = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {len(updates)} | {updates}"
        print(log)
        for update in updates:
            event: NewMessageEvent = EventParser.parse(update)
            if event.code == 4:
                answer = await vk.send_message(event.peer_id, 'Hello, ' + event.extra_fields[2])
                print(answer)

if __name__ == "__main__":
    asyncio.run(main())
