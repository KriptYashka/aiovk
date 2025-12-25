from magic_filter import F

from core.bot_longpool import VkBotMessageEvent
from core.router import Router

from routers.main_router import router as main_router

dispatcher = Router()
routers = [
    main_router,
]
dispatcher.include_routers(*routers)
