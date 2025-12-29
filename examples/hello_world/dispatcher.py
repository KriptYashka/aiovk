from routers.main_router import router as main_router

from core.handlers.router import Router

dispatcher = Router()
routers = [
    main_router,
]
dispatcher.include_routers(*routers)
