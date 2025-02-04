import os
import logging
import jwt
import asyncio
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)

# ✅ Apply Fix for Event Loop Issues
nest_asyncio.apply()

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot 2 Token
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"

# ✅ Secret Key (Must match Bot 1's Secret Key)
SECRET_KEY = "supersecret"

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Allowed Users List
allowed_users = set()

# ✅ Start Command
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args  

    if not args:
        await update.message.reply_text("❌ Invalid or missing link. Please request a new one.")
        return

    try:
        decoded_data = jwt.decode(args[0], SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception as e:
        await update.message.reply_text("❌ Failed to decode link. Please request a new one.")
        return

    if user_id in allowed_users:
        await update.message.reply_text(
            f"🚀 You have already granted permission!\n\nClick below to join the channel:\n{channel_invite_link}"
        )
    else:
        keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data=f"grant_access:{args[0]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup)

# ✅ Handle Button Click
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    args = query.data.split(":")  
    encrypted_link = args[1] if len(args) > 1 else None

    if not encrypted_link:
        await query.answer("❌ Invalid request.")
        return

    try:
        decoded_data = jwt.decode(encrypted_link, SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception as e:
        await query.answer("❌ Failed to decode link.")
        return

    allowed_users.add(user_id)
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")

    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")

# ✅ Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

# ✅ Fix "Bot Already Running" Issue
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    try:
        await app.run_polling()
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())  # ✅ Prevents event loop issues
