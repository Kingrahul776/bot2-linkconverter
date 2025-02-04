import os
import logging
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token (Replace with actual)
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
API_URL = "https://kingcryptocalls.com/store_user"

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Start Command
async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data="grant_permission")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚀 Click the button below to allow message access!", reply_markup=reply_markup)

# ✅ Handle Permission Request
async def handle_permission(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    first_name = query.from_user.first_name
    
    payload = {"user_id": str(user_id), "username": username, "first_name": first_name}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        data = response.json()

        if data["success"]:
            await query.message.reply_text("✅ Permission granted! You will receive updates from us.")
        else:
            await query.message.reply_text(f"❌ {data['message']}")
    except Exception as e:
        logger.error(f"Error saving user permission: {e}")
        await query.message.reply_text("⚠️ Error granting permission. Please try again later.")

# ✅ Broadcast Message to All Users
async def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id != 6142725643:
        await update.message.reply_text("❌ You are not authorized to send broadcasts.")
        return
    
    message = update.message.text.replace("/broadcast", "").strip()
    
    if not message:
        await update.message.reply_text("❌ Please provide a message to broadcast.")
        return
    
    user_list = []  # Load user IDs from your database/API
    
    for user_id in user_list:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")

    await update.message.reply_text("✅ Broadcast sent!")

# ✅ Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_permission, pattern="grant_permission"))
app.add_handler(CommandHandler("broadcast", broadcast))

# ✅ Run Bot
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except RuntimeError:
        logger.warning("⚠️ Event loop already running. Using alternative method.")
        loop = asyncio.get_event_loop()
        loop.create_task(run_bot())
        loop.run_forever()
