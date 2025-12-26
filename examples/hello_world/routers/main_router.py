from core.bot.bot_events import VkBotMessageEvent, VkBotEvent
from core.handlers.router import Router
from core.keyboards.keyboards import VkKeyboard, VkKeyboardColor

router = Router()

@router.message()
async def handle_message(event: VkBotMessageEvent, *args, **kwargs):
    kb = VkKeyboard(inline=True)
    kb.add_callback_button("Test", VkKeyboardColor.POSITIVE, payload={"hello": "world"})
    await event.answer(f"Hello, {event.message.text}", keyboard=kb)

@router.callback_query()
async def handle_callback(event: VkBotEvent, *args, **kwargs):
    await event.event_answer()
    kb = VkKeyboard(inline=True)
    kb.add_callback_button("Test1", VkKeyboardColor.POSITIVE)
    kb.add_callback_button("Test2", VkKeyboardColor.NEGATIVE)
    kb.add_callback_button("Test3", VkKeyboardColor.PRIMARY )
    await event.answer(f"Нажата кнопка {event}", keyboard=kb)