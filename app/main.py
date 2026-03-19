from fastapi import FastAPI
from app.controllers.pages import page_controller
from app.controllers.api import auth_controller, user_controller
from app.exceptions import handler
from app.core import lifespan
from app.core.middlewares import static_middleware
from app.core.middlewares import cors_middleware, security_middleware
import uvicorn
from app.core.config import CONFIG

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.gzip import GZipMiddleware
from app.core.rate_limit import limiter

app = FastAPI(lifespan=lifespan.lifespan)
api = FastAPI(lifespan=lifespan.lifespan)

handler.add_html(app)
handler.add_json(api)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
api.state.limiter = limiter
api.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

security_middleware.add(app)
security_middleware.add(api)
app.add_middleware(GZipMiddleware, minimum_size=1000)
api.add_middleware(GZipMiddleware, minimum_size=1000)

static_middleware.add(app)
cors_middleware.add(api)

app.include_router(page_controller.router)

api.include_router(auth_controller.router)
api.include_router(user_controller.router)


app.mount("/api", api)

if __name__ == "__main__":
    uvicorn.run(app, host=CONFIG.SERVICE_HOST, port=CONFIG.SERVICE_PORT)
