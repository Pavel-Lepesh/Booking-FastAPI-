import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin, ModelView
from starlette.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.rooms.router import router as rooms_router  # noqa
from app.hotels.router import router as hotel_router
from app.images.router import router as router_images
from app.pages.router import router as router_pages
from app.users.router import router as router_users
from app.importer.router import router as router_import
from app.prometheus.router import router as router_prometheus
from app.logger import logger
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DNS,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


app = FastAPI(lifespan=lifespan)

app = VersionedFastAPI(app,
                       version_format='{major}',
                       prefix_format='/v{major}',
                       # description='Greet users with a nice message',
                       # middleware=[
                       #     Middleware(SessionMiddleware, secret_key='mysecretkey')
                       # ]
                       )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("Request execution time", extra={
        "process_time": round(process_time, 4)
    })
    return response


app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(hotel_router)
app.include_router(router_pages)
app.include_router(router_images)
app.include_router(router_import)
app.include_router(router_prometheus)

origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)


app.mount("/static", StaticFiles(directory="app/static"), "static")

if __name__ == "__main__":
    import os.path
    import sys

    import uvicorn

    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    uvicorn.run(
        app="app.main:app",
        reload=True,
    )
