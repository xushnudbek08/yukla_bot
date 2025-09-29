from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from base import get_channels
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton





ADMIN_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔧 Kanal qo`shish", callback_data="add_channel")],
        [InlineKeyboardButton(text="📋 Kanal ro'yxati", callback_data="list_channels")],
        [InlineKeyboardButton(text="❌ Kanal o'chirish", callback_data="delete_channel")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="✉️ Xabar yuborish", callback_data="send_message")],
    ]
)


send = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📃 Text xbar yuborish", callback_data="send_text")],
        [InlineKeyboardButton(text="🌇 Photo xabar yuborish", callback_data="send_photo")],
        [InlineKeyboardButton(text="🎥 Video xabar yuborish", callback_data="send_video")],
        

    ]
)



async def check_subscription(bot: Bot, user_id: int):
    channels = get_channels()
    not_subscribed = []

    for channel_id, link in channels:
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ["left", "kicked"]:
                not_subscribed.append((channel_id, link))
        except (TelegramForbiddenError, TelegramBadRequest):
            # bot kanalga qo‘shilmagan yoki kanal id noto‘g‘ri bo‘lsa o'tkazib yuboramiz
            continue

    if not_subscribed:
        # Tugmalarni massiv sifatida yaratamiz
        buttons = [
            [InlineKeyboardButton(text="📢 Подписаться", url=link)]
            for _, link in not_subscribed
        ]
        # Tekshirish tugmasini qo‘shamiz
        buttons.append([InlineKeyboardButton(text="✅ Проверить", callback_data="check_subs")])

        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        return False, kb

    return True, None

