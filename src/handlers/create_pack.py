import secrets

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InputSticker, Message

from database import SessionLocal
from models import StickerPack, User

router = Router()


class CreatePack(StatesGroup):
    waiting_for_name = State()
    waiting_for_sticker = State()


@router.callback_query(F.data == "create_pack")
async def process_create_pack(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Please enter a name for your new sticker pack 📝")
    await state.set_state(CreatePack.waiting_for_name)
    await query.answer()


@router.message(CreatePack.waiting_for_name)
async def process_pack_name(message: Message, state: FSMContext):
    pack_name = message.text.strip()

    async with SessionLocal() as session:
        result = await session.execute(
            StickerPack.__table__.select()
            .where(StickerPack.user_id == message.from_user.id)
            .where(StickerPack.name == pack_name)
        )
        existing = result.first()

        if existing:
            await message.answer(
                "⚠️ You already have a sticker pack with this name. Please choose another one."
            )
            return

        await state.update_data(pack_name=pack_name)

    await message.answer("Now send me a sticker to add as the first one in your pack 🖼")
    await state.set_state(CreatePack.waiting_for_sticker)


@router.message(CreatePack.waiting_for_sticker, F.sticker)
async def process_first_sticker(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    pack_name = data.get("pack_name")

    short_name = f"{message.from_user.username or message.from_user.id}_{secrets.token_hex(4)}_by_{(await bot.me()).username}"
    title = pack_name

    if message.sticker.is_animated:
        sticker_format = "animated"
    elif message.sticker.is_video:
        sticker_format = "video"
    else:
        sticker_format = "static"

    try:
        await bot.create_new_sticker_set(
            user_id=message.from_user.id,
            name=short_name,
            title=title,
            stickers=[
                InputSticker(
                    sticker=message.sticker.file_id,
                    emoji_list=["😀"],
                    format=sticker_format,
                )
            ],
        )
    except Exception as error:
        await message.answer(f"❌ Failed to create sticker pack: {error}")
        await state.clear()
        return

    async with SessionLocal() as session:
        user = await session.get(User, message.from_user.id)

        if not user:
            user = User(id=message.from_user.id)
            session.add(user)
            await session.commit()

        new_pack = StickerPack(name=pack_name, short_name=short_name, user_id=user.id)
        session.add(new_pack)
        await session.commit()

    await message.answer(
        f"✅ Sticker pack **{pack_name}** created successfully!\n"
        f"👉 [Open pack](https://t.me/addstickers/{short_name})",
    )
    await state.clear()


@router.message(CreatePack.waiting_for_sticker)
async def process_non_sticker(message: Message):
    await message.answer("⚠️ Please send a *sticker*, not text or image.")
