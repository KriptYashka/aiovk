from typing import Any

from core.bot_longpool import VkBotMessageEvent
from core.router import Router

router = Router()

@router.message()
async def handle_message(event: VkBotMessageEvent, **kwargs: Any) -> None:
    print("Received message")