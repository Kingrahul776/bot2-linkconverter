import os
import logging
import asyncio
import jwt  # ✅ Import JWT for encrypted links
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "supersecret"  # Must be the same as used in the Web API

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command - Handles Redirection Flow
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args  # Get the token from /start

    if not args:
        await update.message.reply_text("❌ Invalid or missing token. Please request a new link.")
        return

    encrypted_token = args[0]

    # 🔓 Decode the encrypted token
    try:
        decoded_data = jwt.decode(encrypted_token, SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception as e:
        await update.message.reply_text("❌ Failed to decode link. Please request a new one.")
        return

    if user_id in allowed_users:
        # ✅ User already granted permission, redirect them immediately
        await update.message.reply_text(f"🚀 You have already granted permission!\n\nClick below to join the channel:\n{channel_invite_link}")
    else:
        # ❌ User has not granted permission, show the button
        keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data=f"grant_access:{encrypted_token}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup)

# ✅ Handle Button Click - Grant Access & Redirect
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    args = query.data.split(":")
    encrypted_token = args[1] if len(args) > 1 else None

    if not encrypted_token:
        await query.answer("❌ Invalid request.")
        return

    # 🔓 Decode the encrypted token again
    try:
        decoded_data = jwt.decode(encrypted_token, SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception as e:
        await query.answer("❌ Failed to decode link.")
        return

    allowed_users.add(user_id)
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")

    # ✅ Redirect user to the correct channel
    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")

# ✅ Add Handlers
app = Application.builder().token("YOUR_BOT2_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

# ✅ Fix Event Loop Issue & Run Bot
import nest_asyncio
nest_asyncio.apply()

async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_running():
        logger.warning("⚠️ Event loop already running. Using alternative method.")
        loop.create_task(run_bot())
    else:
        asyncio.run(run_bot())  # ✅ Runs properly if no loop is running
