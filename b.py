import re
import os
import tempfile
import asyncio
import uuid
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import yt_dlp

from config import  BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# URL regex (YouTube, Instagram, TikTok uchun)
URL_RE = re.compile(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|instagram\.com|tiktok\.com)[^\s]+)')

# URLlarni vaqtincha saqlash (id -> url)
URL_STORAGE = {}


# 📥 Yuklab olish funksiyasi
async def download_media(url: str, mode: str):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, f"%(title)s.%(ext)s")

    # umumiy opsiyalar
    ydl_opts = {
        "outtmpl": output_path,
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
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
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
        elif mode == "mp4" and not filename.endswith(".mp4"):
            new_filename = filename.rsplit(".", 1)[0] + ".mp4"
            os.rename(filename, new_filename)
            filename = new_filename

        return filename
    except Exception as e:
        print("Xatolik:", e)
        return None


# /start komandasi
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Salom!\nMenga YouTube, Instagram yoki TikTok link yuboring.\n"
        "Men sizga 🎵 Musiqa yoki 🎬 Video qilib beraman."
    )


# URL yuborilganda tugmalar chiqadi
@dp.message(F.text.regexp(URL_RE))
async def ask_format(message: types.Message):
    url = message.text.strip()
    uid = str(uuid.uuid4())[:8]  # qisqa ID yaratamiz
    URL_STORAGE[uid] = url       # URLni saqlab qo‘yamiz

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Musiqa (MP3)", callback_data=f"mp3|{uid}")],
        [InlineKeyboardButton(text="🎬 Video (MP4)", callback_data=f"mp4|{uid}")],
    ])
    await message.answer("📥 Qaysi formatda yuklab olmoqchisiz?", reply_markup=kb)


# Tugma bosilganda yuklab olish
@dp.callback_query(F.data)
async def handle_download(call: CallbackQuery):
    mode, uid = call.data.split("|", 1)
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
    del URL_STORAGE[uid]  # URLni o‘chirib tashlaymiz (xotirani tozalash uchun)


# Polling ishga tushirish
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
