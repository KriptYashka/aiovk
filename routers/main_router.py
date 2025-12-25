from magic_filter import F

from core.bot_longpool import VkBotMessageEvent
from core.router import Router

router = Router()

@router.message()
async def handle_message(event: VkBotMessageEvent, *args, **kwargs):
    await event.answer(f"Hello, {event.message.text}")
