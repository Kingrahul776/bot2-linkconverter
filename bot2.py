import os
import logging
import asyncio
import requests
import nest_asyncio  # ✅ Fixes event loop issues
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token & Admin ID
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
ADMIN_ID = 6142725643  # Replace with your Telegram ID

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command (Asks for Permission)
async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data="grant_access")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup)

# ✅ Handle Button Click (Grant Access)
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "grant_access":
        allowed_users.add(user_id)
        await query.answer("✅ Permission granted!")
        await query.message.edit_text("✅ You have granted permission!")

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
    nest_asyncio.apply()  # ✅ Fixes event loop issue
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.run_forever()
