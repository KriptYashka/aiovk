import random
import string

from magic_filter import F

from core.bot.bot_events import VkBotCallbackEvent, VkBotMessageEvent
from core.handlers.router import Router
from core.keyboards.keyboards import VkKeyboard, VkKeyboardColor

router = Router()

@router.message(F.message.text.regexp(r'^\d+$'))
async def handle_symbol_count(event: VkBotMessageEvent, *args, **kwargs):
    try:
        symbol_count = int(event.message.text)

        if symbol_count < 1 or symbol_count > 10000:
            await event.answer("Пожалуйста, введите число от 1 до 10000")
            return

        generated_text = "<br>".join([f"Ном. Строки: {i:03}" for i in range(1000)])

        generated_text = generated_text[:symbol_count]

        kb = VkKeyboard(inline=True)
        kb.add_callback_button("Regenerate", VkKeyboardColor.POSITIVE, payload={
            "action": "regenerate_text",
            "symbol_count": symbol_count
        })

        await event.answer(generated_text)

    except ValueError:
        await event.answer("Пожалуйста, введите корректное число")


@router.callback_query(F.payload.get("action") == "regenerate_text")
async def handle_regenerate_text(event: VkBotCallbackEvent, *args, **kwargs):
    symbol_count = event.payload.get("symbol_count", 10)

    generated_text = ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=symbol_count))

    kb = VkKeyboard(inline=True)
    kb.add_callback_button("Regenerate", VkKeyboardColor.POSITIVE, payload={
        "action": "regenerate_text",
        "symbol_count": symbol_count
    })

    await event.event_answer()
    await event.answer(generated_text, keyboard=kb)
