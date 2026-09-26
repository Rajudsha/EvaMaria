import os
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]
CHANNELS = int(os.environ.get("CHANNELS"))
PORT = int(os.environ.get("PORT", 8080))

app = Client("FileStoreBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dummy web server Render ke port check ko pass karne ke liye
async def web_handler(request):
    return web.Response(text="Bot is running!")

@app.on_message(filters.command("start"))
async def start(bot, message):
    if len(message.command) > 1:
        msg_id = int(message.command[1])
        try:
            await bot.copy_message(chat_id=message.from_user.id, from_chat_id=CHANNELS, message_id=msg_id)
        except Exception as e:
            await message.reply_text(f"Error: {e}")
    else:
        await message.reply_text("Bot live hai! File bhejo link lene ke liye.")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def save_file(bot, message):
    if message.from_user.id not in ADMINS:
        return await message.reply_text("Sirf admin file store kar sakta hai!")
    
    forwarded = await message.forward(chat_id=CHANNELS)
    bot_info = await bot.get_me()
    share_link = f"https://t.me/{bot_info.username}?start={forwarded.id}"
    
    await message.reply_text(
        f"File store ho gayi!\n\nLink: {share_link}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Link", url=share_link)]])
    )

async def main():
    server = web.Server(web_handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    await app.start()
    print("Bot Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
