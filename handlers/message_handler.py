# from keyboards.main_keyboard import create_main_keyboard

async def handle_message(vk, message):
    user_id = message['from_id']
    text = message.get('text', '')

    if text.lower() == 'start':
        # keyboard = create_main_keyboard()
        await vk.send_message(user_id, 'Hello, World!')
    else:
        await vk.send_message(user_id, 'Unknown command')
