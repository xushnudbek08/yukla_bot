import re
import os
import tempfile
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
import yt_dlp

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# URL aniqlash regex
URL_RE = re.compile(r'https?://[^\s]+')


# 📥 Yuklab olish funksiyasi
async def download_media(url: str, ext: str = "mp4"):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, f"%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": ext,
        # Cookie ishlatish (YouTube uchun kerak)
        "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
    }

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)
        )

        filename = yt_dlp.YoutubeDL(ydl_opts).prepare_filename(info)
        if not filename.endswith(ext):
            new_filename = filename.rsplit(".", 1)[0] + f".{ext}"
            os.rename(filename, new_filename)
            filename = new_filename

        return filename
    except Exception as e:
        print("Xatolik:", e)
        return None


# /start komandasi
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Salom!\nMenga YouTube, Instagram yoki TikTok link yuboring – men uni yuklab beraman 📥")


# URL yuborilganda
@dp.message(F.text.regexp(URL_RE))
async def handle_url(message: types.Message):
    url = message.text.strip()
    await message.answer("⏳ Yuklab olinmoqda, kuting...")

    filename = await download_media(url, "mp4")

    if filename and os.path.exists(filename):
        video = FSInputFile(filename)
        await message.answer_video(video, caption="✅ Tayyor!")
        os.remove(filename)
    else:
        await message.answer("❌ Yuklab olishda xatolik bo‘ldi.")


# Polling ishga tushirish
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
