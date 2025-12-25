from core.bot.bot_events import VkBotMessageEvent
from core.handlers.router import Router

router = Router()

@router.message()
async def handle_message(event: VkBotMessageEvent, *args, **kwargs):
    await event.answer(f"Hello, {event.message.text}")
