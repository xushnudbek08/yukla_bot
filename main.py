import asyncio
import logging
from aiogram import Bot, Dispatcher ,F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN
from heandlers.register import register
from heandlers.admin import admin_router
from heandlers.yukla import yukla

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)




dp.include_router(register),
dp.include_router(admin_router)
dp.include_router(yukla)









async def main():
    for admin in ADMIN:
        try:
            await bot.send_message(chat_id=admin, text="Бот запущен")
        except Exception as e:
            print(f"Error sending message to {admin}: {e}")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        print("toxtadi")