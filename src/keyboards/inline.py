from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Create pack", callback_data="create_pack"),
            InlineKeyboardButton(text="📂 My packs", callback_data="my_packs"),
        ],
    ]
)


def pack_actions_keyboard(short_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Finish", callback_data="finish_adding"),
                InlineKeyboardButton(
                    text="📂 Open pack", url=f"https://t.me/addstickers/{short_name}"
                ),
            ]
        ]
    )
