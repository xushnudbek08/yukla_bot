from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from base import add_channel,get_channels,remove_channel,blocked_users_count,total_users_count,get_all_chat_ids
from config import ADMIN
from aiogram.types import CallbackQuery
from keyboards import send
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
admin_router = Router()






@admin_router.callback_query(F.data =="")





class photoxbar(StatesGroup):
    photo = State()
    captions = State()


@admin_router.callback_query(F.data == "send_photo")
async def send_photo(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("Yubormoqchi bolgan rasmingzini yuboring:")
    await state.set_state(photoxbar.photo)



@admin_router.message(photoxbar.photo)
async def get_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Rasm yuboring, video emas!")
        return

    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)

    await message.answer("✍️ Endi rasmga qo‘shiladigan matn (caption) yuboring:")
    await state.set_state(photoxbar.captions)




@admin_router.message(photoxbar.captions)
async def process_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    photo = data.get("photo")
    caption_text = message.text

    users = get_all_chat_ids()
    success_count = 0
    fail_count = 0

    for user_id in users:
        try:
            await message.bot.send_photo(user_id, photo=photo, caption=caption_text)
            success_count += 1
        except Exception as e:
            print(f"Xatolik {user_id} ga video yuborishda: {e}")
            fail_count += 1

    await message.answer(
        f"✅ Rasm yuborildi!\n"
        f"📤 Muvaffaqiyatli: {success_count}\n"
        f"❌ Muvaffaqiyatsiz: {fail_count}"
    )

    await state.clear()









class VideoXabar(StatesGroup):
    video = State()
    caption = State()


# Boshlash
@admin_router.callback_query(F.data == "send_video")
async def broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🎬 Yubormoqchi bo‘lgan videongizni yuboring:")
    await state.set_state(VideoXabar.video)


# Video olish
@admin_router.message(VideoXabar.video)
async def get_video(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❌ Video yuboring!")
        return

    # videoni state ichiga saqlaymiz
    await state.update_data(video=message.video.file_id)

    await message.answer("✍️ Endi videoga qo‘shiladigan matn (caption) yuboring:")
    await state.set_state(VideoXabar.caption)


# Caption olish va video yuborish
@admin_router.message(VideoXabar.caption)
async def process_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    video_file_id = data.get("video")
    caption_text = message.text

    users = get_all_chat_ids()
    success_count = 0
    fail_count = 0

    for user_id in users:
        try:
            await message.bot.send_video(user_id, video=video_file_id, caption=caption_text)
            success_count += 1
        except Exception as e:
            print(f"Xatolik {user_id} ga video yuborishda: {e}")
            fail_count += 1

    await message.answer(
        f"✅ Video yuborildi!\n"
        f"📤 Muvaffaqiyatli: {success_count}\n"
        f"❌ Muvaffaqiyatsiz: {fail_count}"
    )

    await state.clear()







class Xabar(StatesGroup):
    broadcast_message = State()


# Boshlanishi
@admin_router.callback_query(F.data == "send_text")
async def broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📨 Xabar matnini kiriting:")
    await state.set_state(Xabar.broadcast_message)


# Xabar yozilganda
@admin_router.message(Xabar.broadcast_message)
async def process_broadcast(message: Message, state: FSMContext):
    text = message.text
    users = get_all_chat_ids()  # bu siz yozgan funksiya
    success_count = 0
    fail_count = 0

    for user_id in users:
        try:
            await message.bot.send_message(user_id, text)
            success_count += 1
        except Exception as e:
            print(f"Xatolik {user_id} ga xabar yuborishda: {e}")
            fail_count += 1

    await message.answer(
        f"✅ Xabar yuborildi!\n"
        f"📤 Muvaffaqiyatli: {success_count}\n"
        f"❌ Muvaffaqiyatsiz: {fail_count}"
    )
    await state.clear()


@admin_router.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN:
        return await callback.message.answer("⛔ Siz admin emassiz!")
    
    total_users = total_users_count()
    blocked_users = blocked_users_count()

    response = (
        f"📊 Bot statistikasi:\n\n"
        f"👥 Foydalanuvchilar soni: {total_users}\n"
        f"🚫 Bloklangan foydalanuvchilar: {blocked_users}\n"
    )
    await callback.message.answer(response)




class RemoveChannel(StatesGroup):
    remove_channel = State()


@admin_router.callback_query(F.data == "delete_channel")
async def delete_channel_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN:
        return await callback.message.answer("⛔ Siz admin emassiz!")
    
    channels = get_channels()
    if not channels:
        return await callback.message.answer("📢 Hozircha kanal qo‘shilmagan.")
    
    response = "❌ O‘chirish uchun kanal tartib raqamini yuboring:\n\n"
    for idx, (channel_id, channel_link) in enumerate(channels, start=1):
        response += f"{idx}. ID: `{channel_id}`\n   Link: {channel_link}\n\n"
    
    # Kanallarni state ichida saqlaymiz
    await state.update_data(channels=channels)
    await callback.message.answer(response)
    await state.set_state(RemoveChannel.remove_channel)


@admin_router.message(RemoveChannel.remove_channel)
async def process_remove_channel(message: Message, state: FSMContext):
    data = await state.get_data()
    channels = data.get("channels", [])
    
    try:
        index = int(message.text.strip()) - 1  # foydalanuvchi raqam yuboradi
        if index < 0 or index >= len(channels):
            return await message.answer("⚠️ Noto‘g‘ri raqam yuborildi.")
        
        channel_id, channel_link = channels[index]
        remove_channel(channel_id)  # bazadan o‘chiradi
        
        await message.answer(
            f"✅ Kanal o‘chirildi!\n\n📢 ID: `{channel_id}`\n🔗 Link: {channel_link}"
        )
    except ValueError:
        await message.answer("⚠️ Faqat raqam yuboring.")
    
    await state.clear()



@admin_router.callback_query(F.data == "list_channels")
async def list_channels(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN:
        return await callback.message.answer("⛔ Siz admin emassiz!")
    
    channels = get_channels()
    if not channels:
        return await callback.message.answer("📢 Hozircha kanal qo‘shilmagan.")
    
    response = "📋 Kanal ro'yxati:\n\n"
    for idx, (channel_id, channel_link) in enumerate(channels, start=1):
        response += f"{idx}. ID: `{channel_id}`\n   Link: {channel_link}\n\n"
    
    await callback.message.answer(response)





@admin_router.callback_query(F.data == "send_message")
async def send_message_options(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN:
        return await callback.message.answer("⛔ Siz admin emassiz!")
    
    await callback.message.answer(
        "📢 Xabar yuborish turini tanlang:", 
        reply_markup=send   # bu yerda send - InlineKeyboardMarkup bo‘lishi kerak
    )


class AddChannel(StatesGroup):
    channel_id = State()
    channel_link = State()


# 🔹 Inline tugma bosilganda ishlaydi
@admin_router.callback_query(F.data == "add_channel")
async def cmd_add_channel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN:
        return await callback.message.answer("⛔ Siz admin emassiz!")
    
    await callback.message.answer(
        "📢 Yangi kanal qo‘shish\n\n➡️ Avval kanal ID yuboring (masalan: `-1001234567890`):"
    )
    await state.set_state(AddChannel.channel_id)


# 🔹 Kanal ID qabul qilish
@admin_router.message(AddChannel.channel_id)
async def add_channel_id(message: Message, state: FSMContext):
    await state.update_data(channel_id=message.text.strip())
    await message.answer(
        "🔗 Endi kanal linkini yuboring (masalan: `https://t.me/kanal_nomi`):"
    )
    await state.set_state(AddChannel.channel_link)


# 🔹 Kanal linkini qabul qilish
@admin_router.message(AddChannel.channel_link)
async def add_channel_link(message: Message, state: FSMContext):
    data = await state.get_data()
    channel_id = data["channel_id"]
    channel_link = message.text.strip()

    add_channel(channel_id, channel_link)

    await message.answer(
        f"✅ Kanal qo‘shildi!\n\n📢 ID: `{channel_id}`\n🔗 Link: {channel_link}"
    )
    await state.clear()