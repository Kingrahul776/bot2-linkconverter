import os
import logging
import asyncio
import jwt  # ✅ Import JWT for encrypted links
import nest_asyncio  # ✅ Fixes event loop issues!
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)

# ✅ Apply fix for "RuntimeError: Event loop is already running"
nest_asyncio.apply()

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token & Secret Key (Ensure it matches the API)
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"  # Replace with your actual Bot 2 token
SECRET_KEY = "supersecret"  # Ensure this matches the key used in your web API

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command (Handles Redirection)
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args  # Get the start parameter

    if not args or len(args) == 0:
        await update.message.reply_text("❌ Invalid link. Please request a new one.")
        return

    try:
        # 🔓 Decode the encrypted link
        decoded_data = jwt.decode(args[0], SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data.get("link")

        if not channel_invite_link:
            raise ValueError("No link found in token.")

        if user_id in allowed_users:
            # ✅ User has already granted permission, redirect them to the channel
            await update.message.reply_text(f"🚀 You have already granted permission!\n\nClick below to join the channel:\n{channel_invite_link}")
        else:
            # ❌ User has not granted permission, ask for confirmation
            keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data=f"grant_access:{args[0]}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup)

    except jwt.ExpiredSignatureError:
        await update.message.reply_text("❌ Link expired! Request a new one.")
    except jwt.InvalidTokenError:
        await update.message.reply_text("❌ Invalid link! Try again.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error decoding link: {str(e)}")

# ✅ Handle Button Click (Grant Access & Redirect)
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    args = query.data.split(":")  # Extract the encrypted link
    encrypted_link = args[1] if len(args) > 1 else None

    if not encrypted_link:
        await query.answer("❌ Invalid request.")
        return

    try:
        # 🔓 Decode the encrypted link again
        decoded_data = jwt.decode(encrypted_link, SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data.get("link")
    except Exception as e:
        await query.answer("❌ Failed to decode link.")
        return

    # ✅ Grant Permission & Redirect
    allowed_users.add(user_id)
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")

    # ✅ Redirect user to the correct channel
    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")

# ✅ Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

# ✅ Fix Event Loop Issue & Run Bot
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())  # ✅ Fix event loop issues
