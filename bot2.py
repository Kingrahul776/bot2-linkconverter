import os
import logging
import asyncio
import jwt  # ✅ JWT for encrypted invite links
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token & Admin ID
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
ADMIN_ID = 6142725643  # ✅ Set Admin ID for broadcasting

# ✅ Secret Key (SAME as Bot 1)
SECRET_KEY = "supersecret"

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command - Handles Mini-App Redirection
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args  # Get the start parameter

    if not args:
        await update.message.reply_text("❌ Invalid link. Please request a new one.")
        return

    # 🔓 Decode the encrypted link
    try:
        decoded_data = jwt.decode(args[0], SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception:
        await update.message.reply_text("❌ Failed to decode link. Please request a new one.")
        return

    if user_id in allowed_users:
        # ✅ User has already granted permission
        await update.message.reply_text(
            f"🚀 You have already granted permission!\n\nClick below to join the channel:\n{channel_invite_link}"
        )
    else:
        # ❌ User has NOT granted permission
        keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data=f"grant_access:{args[0]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup
        )

# ✅ Handle Button Click - Grant Access & Redirect
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    args = query.data.split(":")  # Extract the encrypted link
    encrypted_link = args[1] if len(args) > 1 else None

    if not encrypted_link:
        await query.answer("❌ Invalid request.")
        return

    # 🔓 Decode the encrypted link
    try:
        decoded_data = jwt.decode(encrypted_link, SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception:
        await query.answer("❌ Failed to decode link.")
        return

    allowed_users.add(user_id)
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")

    # ✅ Redirect user to the correct channel
    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")

# ✅ Broadcast Message (Admin Only)
async def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    message = update.message.text.replace("/broadcast ", "")
    if not message:
        await update.message.reply_text("⚠️ Please provide a message to broadcast.")
        return

    success_count = 0
    for user_id in allowed_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Failed to send message to {user_id}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {success_count} users.")

# ✅ Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(CommandHandler("broadcast", broadcast))

# ✅ Fix Event Loop Issue & Run Bot
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    try:
        # Check if an event loop is already running
        loop = asyncio.get_running_loop()
        if loop.is_running():
            logger.warning("⚠️ Event loop already running. Running bot in a new task.")
            loop.create_task(run_bot())
        else:
            # If no loop is running, run the bot normally
            loop.run_until_complete(run_bot())
    except RuntimeError as e:
        # Handle cases where no event loop is available
        if "no running event loop" in str(e):
            asyncio.run(run_bot())
        else:
            logger.error(f"❌ Unexpected error: {e}")
