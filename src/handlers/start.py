from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.inline import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Welcome! Choose an option:", reply_markup=main_menu)
