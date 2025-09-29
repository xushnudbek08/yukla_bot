from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message,ChatMemberUpdated
from aiogram import F
from base import get_user, add_user , block_user, unblock_user
from config import ADMIN
from keyboards import ADMIN_inline_kb, check_subscription
from aiogram import Bot
from aiogram.types import CallbackQuery
register = Router()





@register.message(CommandStart())
async def command_start(message: Message,bot: Bot):
    full_name = message.from_user.full_name
    user_id = message.from_user.id
    username = message.from_user.username
    Chat_id = message.chat.id
    user = get_user(user_id)
    add_userr= add_user(user_id, full_name, username,Chat_id)

    if user:
        if user_id in ADMIN:
            await message.answer(f"Qaytganingizdan xursandmiz, {full_name}!\nSiz adminisztratorsiz!", reply_markup=ADMIN_inline_kb)
        
        else:
            ok, kb = await check_subscription(bot, message.from_user.id)
            if not ok:
                await message.answer("❗ Подпишитесь на каналы, чтобы продолжить:", reply_markup=kb)
                return
    # ✅ Obuna bo'lsa shu yerda asosiy kod bajariladi
            await message.answer("✅ Вы подписаны, продолжим!")
            await message.answer(f"Qaytganingizdan xursandmiz, {full_name}!")


    else:
        if user_id in ADMIN:
            add_userr
            await message.answer(f"Xush kelibsiz, {full_name}!\nSiz adminisztratorsiz!", reply_markup=ADMIN_inline_kb)
        
        else:
            ok, kb = await check_subscription(bot, message.from_user.id)
            if not ok:
                await message.answer("❗Davom etish uchun kanalga obuna bo'ling:", reply_markup=kb)
                return
    # ✅ Obuna bo'lsa shu yerda asosiy kod bajariladi
            await message.answer("✅ Obuna bo'ldingiz, davom etamiz!")
            await message.answer(f"Qaytganingizdan xursandmiz, {full_name}!")
            add_userr
            await message.answer(f"Xush kelibsiz, {full_name}!")


@register.callback_query(F.data == "check_subs")
async def recheck_subs(callback: CallbackQuery, bot: Bot):
    ok, kb = await check_subscription(bot, callback.from_user.id)
    if not ok:
        await callback.message.edit_text("❗ Siz hali obuna boʻlmagansiz:", reply_markup=kb)
    else:
        await callback.message.edit_text("✅ Obunangiz tasdiqlandi, endi siz botdan foydalanishingiz mumkin!")















@register.my_chat_member()
async def track_block(update: ChatMemberUpdated):
    new_status = update.new_chat_member.status
    user = update.from_user

    if new_status == "kicked":  # user botni blokladi
        block_user(user.id)
    elif new_status in ["member", "administrator"]:  # user qayta yoqdi
        unblock_user(user.id)

