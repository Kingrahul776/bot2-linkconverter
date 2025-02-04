import os
import logging
import asyncio
import jwt  # ✅ Import JWT for encrypted links
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup  # ✅ Fix Missing Imports
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext  # ✅ Fix Missing Imports
)

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import jwt  # Import JWT library to decode the encrypted link

SECRET_KEY = "your_secret_key"  # Use the same secret key from Bot 1

# ✅ Start Command - Handles Redirection Flow
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
async def button_click(update: Update, context: CallbackContext):
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
