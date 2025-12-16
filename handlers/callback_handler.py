# from keyboards.main_keyboard import create_main_keyboard

async def handle_callback(vk, update):
    user_id = update['object']['user_id']
    payload = update['object']['data']['payload']

    if payload == 'button1':
        # keyboard = create_main_keyboard()
        await vk.send_message(user_id, 'You pressed button 1')
    else:
        await vk.send_message(user_id, 'Unknown callback')
