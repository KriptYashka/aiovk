from magic_filter import F

from core.bot.bot_events import VkBotCallbackEvent, VkBotMessageEvent
from core.handlers.router import Router
from core.keyboards.keyboards import VkKeyboard, VkKeyboardColor

router = Router()


def _parse_count(text: str) -> int | None:
    """
    Ожидает строку вида "inline 10" или "common 7".
    Возвращает количество кнопок или None, если парсинг не удался.
    """
    parts = text.strip().split()
    if len(parts) != 2:
        return None
    _, count_str = parts
    if not count_str.isdigit():
        return None
    return int(count_str)


@router.message(F.message.text.regexp(r"^inline\s+\d+$"))
async def inline_keyboard_cmd(event: VkBotMessageEvent, *args, **kwargs):
    """
    Команда: "inline <n>"

    Возвращает inline‑клавиатуру.
    Кнопки подписаны номерами столбца и ряда (1-2 колонки): "col-row".
    """
    text = event.message.text
    count = _parse_count(text)
    if not count or count <= 0:
        await event.answer("Укажи число кнопок: inline <количество>", keyboard=None)
        return

    buttons_per_row = 5
    kb = VkKeyboard(inline=True)

    for i in range(count):
        row = i // buttons_per_row + 1
        col = i % buttons_per_row + 1
        label = f"{col}-{row}"  # сначала номер столбца, потом ряда

        kb.add_callback_button(
            label,
            VkKeyboardColor.PRIMARY,
            payload={"col": col, "row": row},
        )

        # перенос строки после каждых двух кнопок, кроме последней
        if (i + 1) % buttons_per_row == 0 and (i + 1) < count:
            kb.add_line()

    result = await event.answer(
        f"Inline клавиатура на {count} кнопок (2 столбца).",
        keyboard=kb,
    )

    if "error" in result:
        await event.answer(result["error"])


@router.message(F.message.text.regexp(r"^common\s+\d+$"))
async def common_keyboard_cmd(event: VkBotMessageEvent, *args, **kwargs):
    """
    Команда: "common <n>"

    Возвращает обычную клавиатуру.
    В ряду максимум 5 столбцов.
    """
    text = event.message.text
    count = _parse_count(text)
    if not count or count <= 0:
        await event.answer("Укажи число кнопок: common <количество>", keyboard=None)
        return

    buttons_per_row = 5  # максимум 5 столбцов в ряду
    kb = VkKeyboard(one_time=False, inline=False)

    for i in range(count):
        label = str(i + 1)
        kb.add_callback_button(label, VkKeyboardColor.SECONDARY, payload={"col": i, "row": i // buttons_per_row})

        # перенос строки после каждых пяти кнопок, кроме последней
        if (i + 1) % buttons_per_row == 0 and (i + 1) < count:
            kb.add_line()

    result = await event.answer(
        f"Обычная клавиатура на {count} кнопок (до 5 столбцов в ряду).",
        keyboard=kb,
    )
    if "error" in result:
        code = result["error"]["error_code"]
        msg = result["error"]["error_msg"]
        await event.answer(f"Ошибка {code}\n" + msg)


@router.message(F.message.text.regexp(r"^help$"))
async def help_cmd(event: VkBotMessageEvent, *args, **kwargs):
    """
    Третья команда — подсказка по использованию.
    """
    await event.answer(
        "Примеры команд:\n"
        "inline 4  — inline‑клавиатура, 2 столбца, подписи вида «1-1», «2-1»...\n"
        "common 7  — обычная клавиатура, до 5 кнопок в ряду."
    )


@router.callback_query()
async def handle_any_callback(event: VkBotCallbackEvent, *args, **kwargs):
    """
    Обработчик нажатий на callback‑кнопки: выводит информацию о нажатой кнопке.
    """
    await event.event_answer()

    payload = event.payload
    # payload обычно приходит как dict (см. примеры с F.payload.get(...))
    if isinstance(payload, dict):
        col = payload.get("col")
        row = payload.get("row")
        if col is not None or row is not None:
            await event.answer(f"Нажата callback‑кнопка: col={col}, row={row}\nPayload={payload}")
            return

    await event.answer(f"Нажата callback‑кнопка.\nPayload={payload}")


