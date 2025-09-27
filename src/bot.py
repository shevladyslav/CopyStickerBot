import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
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


async def main():
    register_handlers()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logging.info("Bot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
