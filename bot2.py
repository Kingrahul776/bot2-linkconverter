import os
import logging
import asyncio
import jwt  # ✅ Import JWT for encrypted links
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext, ContextTypes
)

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token (Replace with your Bot 2 token)
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
SECRET_KEY = "supersecret"  # Use the same key from Bot 1 (Flask API)

# ✅ Initialize the bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command - Handles Redirection Flow
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    args = context.args  # Get the start parameter

    if not args:
        await update.message.reply_text("❌ Invalid link. Please request a new one.")
        return

    # 🔓 Decode the encrypted link
    try:
        decoded_data = jwt.decode(args[0], SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception as e:
        await update.message.reply_text("❌ Failed to decode link. Please request a new one.")
        return

    if user_id in allowed_users:
        # ✅ User has already granted permission, send channel invite directly
        await update.message.reply_text(f"🚀 You have already granted permission!\n\nClick below to join the channel:\n{channel_invite_link}")
    else:
        # ❌ User has not granted permission, show button
        keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data=f"grant_access:{args[0]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup)

# ✅ Handle Button Click - Grant Access & Redirect
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    args = query.data.split(":")  # Extract the encrypted link
    encrypted_link = args[1] if len(args) > 1 else None

    if not encrypted_link:
        await query.answer("❌ Invalid request.")
        return

    # 🔓 Decode the encrypted link again
    try:
        decoded_data = jwt.decode(encrypted_link, SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception as e:
        await query.answer("❌ Failed to decode link.")
        return

    allowed_users.add(user_id)
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")

    # ✅ Redirect user to the correct channel
    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")

# ✅ Register Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

# ✅ Run Bot Properly with Async Fix
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

import nest_asyncio  # ✅ Fix event loop errors
nest_asyncio.apply()

# ✅ Fix Event Loop Issue & Run Bot
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    if loop.is_running():
        logger.warning("⚠️ Event loop already running. Using alternative method.")
        loop.create_task(run_bot())  # ✅ Run the bot as an async task
    else:
        asyncio.run(run_bot())  # ✅ Runs properly if no loop is running
