import os
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# ✅ Load bot token from environment variables
BOT2_TOKEN = os.getenv("BOT2_TOKEN")

if not BOT2_TOKEN:
    raise ValueError("🚨 ERROR: BOT2_TOKEN is missing! Set it in Railway.")

# ✅ Print token check (for debugging)
print(f"🚀 Bot 2 starting with token: {BOT2_TOKEN[:5]}********")

# ✅ Function to start bot
async def run_bot():
    app = Application.builder().token(BOT2_TOKEN).build()
    print("🚀 Bot 2 is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(100)

if __name__ == "__main__":
    asyncio.run(run_bot())
