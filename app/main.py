from fastapi import FastAPI
from app.controllers.pages import page_controller
from app.controllers.api import auth_controller, user_controller
from app.exceptions import handler
from app.core import lifespan
from app.core.middlewares import static_middleware
from app.core.middlewares import cors_middleware
import uvicorn
from app.core.config import CONFIG

app = FastAPI(lifespan=lifespan.lifespan)
api = FastAPI(lifespan=lifespan.lifespan)

handler.add_html(app)
handler.add_json(api)

static_middleware.add(app)
cors_middleware.add(api)

app.include_router(page_controller.router)

api.include_router(auth_controller.router)
api.include_router(user_controller.router)


app.mount("/api", api)

if __name__ == "__main__":
    uvicorn.run(app, host=CONFIG.SERVICE_HOST, port=CONFIG.SERVICE_PORT)
