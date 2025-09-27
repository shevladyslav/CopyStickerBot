from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputSticker,
    Message,
)

from database import SessionLocal
from models import StickerPack

router = Router()


class PackStates(StatesGroup):
    selected_pack = State()
    waiting_for_stickers = State()


@router.callback_query(F.data == "my_packs")
async def show_my_packs(query: CallbackQuery, state: FSMContext):
    async with SessionLocal() as session:
        result = await session.execute(
            StickerPack.__table__.select().where(
                StickerPack.user_id == query.from_user.id
            )
        )
        packs = result.fetchall()

    if not packs:
        await query.message.answer("📂 You don't have any sticker packs yet.")
        await query.answer()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=pack.name, callback_data=f"choose_pack:{pack.id}"
                )
            ]
            for pack in packs
        ]
    )

    await query.message.answer(
        "📂 Here are your packs, choose one:", reply_markup=keyboard
    )
    await query.answer()


@router.callback_query(F.data.startswith("choose_pack:"))
async def choose_pack(query: CallbackQuery, state: FSMContext):
    pack_id = int(query.data.split(":")[1])
    await state.update_data(selected_pack=pack_id)
    await state.set_state(PackStates.waiting_for_stickers)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Finish", callback_data="finish_adding")]
        ]
    )

    await query.message.answer(
        "✅ Pack selected! Now send me stickers to add to this pack 🖼\n"
        "Or press *Finish* when you're done.",
        reply_markup=keyboard,
    )
    await query.answer()


@router.message(F.sticker)
async def add_sticker_to_selected_pack(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    pack_id = data.get("selected_pack")

    if not pack_id:
        return

    async with SessionLocal() as session:
        pack = await session.get(StickerPack, pack_id)
        if not pack:
            await message.answer("⚠️ Pack not found. Please choose again.")
            await state.clear()
            return

        if message.sticker.is_animated:
            sticker_format = "animated"
        elif message.sticker.is_video:
            sticker_format = "video"
        else:
            sticker_format = "static"

        try:
            await bot.add_sticker_to_set(
                user_id=message.from_user.id,
                name=pack.short_name,
                sticker=InputSticker(
                    sticker=message.sticker.file_id,
                    emoji_list=["😀"],
                    format=sticker_format,
                ),
            )

            new_set = await bot.get_sticker_set(pack.short_name)
            last_sticker = new_set.stickers[-1]

            await state.update_data(last_sticker_id=last_sticker.file_id)

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌ Delete last sticker",
                            callback_data="delete_last_sticker",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="📂 Open pack",
                            url=f"https://t.me/addstickers/{pack.short_name}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="✅ Finish", callback_data="finish_adding"
                        )
                    ],
                ]
            )

            await message.answer(
                f"✅ Sticker added to pack **{pack.name}**!",
                reply_markup=keyboard,
            )
        except Exception as error:
            await message.answer(f"❌ Failed to add sticker: {error}")


@router.callback_query(F.data == "finish_adding")
async def finish_adding(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.answer("🎉 Done! You’ve finished adding stickers.")
    await query.answer()


@router.callback_query(F.data == "delete_last_sticker")
async def delete_last_sticker(query: CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    last_sticker_id = data.get("last_sticker_id")

    if not last_sticker_id:
        await query.answer("⚠️ No sticker to delete.", show_alert=True)
        return

    try:
        await bot.delete_sticker_from_set(last_sticker_id)
        await state.update_data(last_sticker_id=None)
        await query.message.answer("🗑️ Last sticker has been deleted.")
    except Exception as error:
        await query.message.answer(f"❌ Failed to delete sticker: {error}")

    await query.answer()
