def create_main_keyboard():
    keyboard = {
        "one_time": False,
        "buttons": [
            [
                {
                    "action": {
                        "type": "callback",
                        "payload": "{\"button\": \"button1\"}",
                        "label": "Button 1"
                    },
                    "color": "primary"
                }
            ]
        ]
    }
    return keyboard
