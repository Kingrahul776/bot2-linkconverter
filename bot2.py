import os
import logging
import jwt
import asyncio
import nest_asyncio
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, CallbackContext
)

# ✅ Apply Fix for Event Loop Issues
nest_asyncio.apply()

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot 2 Token & Secret Key
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
SECRET_KEY = "supersecret"  # Must match Bot 1's Secret Key

# ✅ Allowed Users List (To store who granted permission)
allowed_users = set()

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()


# ✅ Step 1: Start Command (Triggers Mini App)
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
        # ✅ If user already gave permission, send the channel link directly
        await update.message.reply_text(f"🚀 You have already granted permission!\n\nClick below to join the channel:\n{channel_invite_link}")
    else:
        # ❌ User has not granted permission → Show Mini App
        keyboard = [[
            InlineKeyboardButton(
                "✅ Grant Permission",
                web_app=WebAppInfo(url="https://t.me/vipsignals221bot")  # Replace with your Mini App URL
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 Welcome! Grant me permission to send messages.", reply_markup=reply_markup)


# ✅ Step 2: Handle Button Click - Grant Permission
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

    allowed_users.add(user_id)  # ✅ Remember user permission
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")

    # ✅ Redirect user to the correct channel
    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")


# ✅ Step 3: Broadcast Command (Admin Only)
async def broadcast(update: Update, context: CallbackContext):
    admin_id = 6142725643  # Replace with your Telegram ID
    if update.message.from_user.id != admin_id:
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


# ✅ Step 4: Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(CommandHandler("broadcast", broadcast))


# ✅ Step 5: Run Bot with Proper Event Loop Handling
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
