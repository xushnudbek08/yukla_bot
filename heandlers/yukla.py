import re
import os
import tempfile
import asyncio
import uuid
from aiogram import types, F, Router, Bot
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keyboards import check_subscription
import yt_dlp

yukla = Router()

# URL regex (YouTube, Instagram, TikTok uchun)
URL_RE = re.compile(
    r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|instagram\.com|tiktok\.com)[^\s]+)'
)

# URLlarni vaqtincha saqlash (id -> url)
URL_STORAGE = {}


# 📥 Yuklab olish funksiyasi
async def download_media(url: str, mode: str):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, f"%(title)s.%(ext)s")

    # umumiy opsiyalar
    ydl_opts = {
        "outtmpl": output_path,
        "noplaylist": True,
        "quiet": True,
        "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    }

    if mode == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:  # video
        ydl_opts.update({
            # cookiesiz ishlashi uchun MP4 formatni cheklaymiz
            "format": "best[ext=mp4][height<=720]/best[ext=mp4]/best",
        })

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)
        )
        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)

        if mode == "mp3":
            filename = filename.rsplit(".", 1)[0] + ".mp3"

        return filename
    except Exception as e:
        print("Xatolik:", e)
        return None


# URL yuborilganda tugmalar chiqadi
@yukla.message(F.text.regexp(URL_RE))
async def ask_format(message: types.Message, bot: Bot):
    ok, kb = await check_subscription(bot, message.from_user.id)
    if not ok:
        await message.answer(
            "❗ Botni ishlatish uchun kanalarga obuna bo‘ling:",
            reply_markup=kb
        )
        return

    # ✅ Obuna bo‘lsa
    await message.answer("✅ Siz obuna bo‘ldingiz, botdan foydalanishingiz mumkin.")

    url = message.text.strip()
    uid = str(uuid.uuid4())[:8]  # qisqa ID yaratamiz
    URL_STORAGE[uid] = url       # URLni saqlab qo‘yamiz

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Musiqa (MP3)", callback_data=f"mp3|{uid}")],
        [InlineKeyboardButton(text="🎬 Video (MP4)", callback_data=f"mp4|{uid}")],
    ])
    await message.answer("📥 Qaysi formatda yuklab olmoqchisiz?", reply_markup=kb)


# Tugma bosilganda yuklab olish
@yukla.callback_query(F.data)
async def handle_download(call: CallbackQuery):
    try:
        mode, uid = call.data.split("|", 1)
    except ValueError:
        await call.answer("❌ Xato format.")
        return

    url = URL_STORAGE.get(uid)
    if not url:
        await call.message.answer("❌ Link muddati o‘tib ketgan.")
        await call.answer()
        return

    await call.message.edit_text(f"⏳ Yuklab olinmoqda... ({mode.upper()})")

    filename = await download_media(url, mode)

    if filename and os.path.exists(filename):
        file = FSInputFile(filename)
        if mode == "mp3":
            await call.message.answer_audio(file, caption="✅ Tayyor! 🎵")
        else:
            await call.message.answer_video(file, caption="✅ Tayyor! 🎬")
        os.remove(filename)
    else:
        await call.message.answer("❌ Yuklab olishda xatolik bo‘ldi.")

    await call.answer()
    URL_STORAGE.pop(uid, None)  # URLni o‘chirib tashlaymiz
