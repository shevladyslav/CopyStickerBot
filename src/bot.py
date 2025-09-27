import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from dotenv import load_dotenv

from database import engine
from handlers import create_pack, my_packs, start
from models import Base

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def register_handlers():
    dp.include_router(start.router)
    dp.include_router(create_pack.router)
    dp.include_router(my_packs.router)


async def on_startup(app: web.Application):
    register_handlers()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    asyncio.create_task(dp.start_polling(bot))


async def on_cleanup(app: web.Application):
    await bot.session.close()


async def healthcheck(request):
    return web.Response(text="Bot is running!")


def main():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    web.run_app(app, port=int(os.getenv("PORT", 8080)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
