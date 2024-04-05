from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.bookings.router import router as router_bookings
from app.users.models import Users
from app.users.router import router as router_users
from app.hotels.router import router as hotel_router
from app.hotels.rooms.router import router as rooms_router
from app.pages.router import router as router_pages
from app.images.router import router as router_images
from app.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin, ModelView
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine=engine)


class UsersAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.email]


admin.add_view(UsersAdmin)


app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(hotel_router)
app.include_router(router_pages)
app.include_router(router_images)

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
