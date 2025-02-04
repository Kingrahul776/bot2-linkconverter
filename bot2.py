import logging
import asyncio
import jwt
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# ✅ Apply fix for nested event loops
nest_asyncio.apply()

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token & Admin ID
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
SECRET_KEY = "supersecret"  # ✅ Same as Web API's secret key
ADMIN_ID = 6142725643  # ✅ Your Telegram ID

# ✅ Initialize Telegram Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command (Handles Mini-App Web Redirection)
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    args = context.args  # Extract Token

    if not args:
        await update.message.reply_text("❌ Invalid link. Please request a new one.")
        return

    try:
        decoded_data = jwt.decode(args[0], SECRET_KEY, algorithms=["HS256"])
        channel_invite_link = decoded_data["link"]
    except Exception:
        await update.message.reply_text("❌ Failed to decode link. Please request a new one.")
        return

    # 🔹 If user has already granted permission, send channel link
    if user_id in allowed_users:
        await update.message.reply_text(f"🚀 You have already granted permission!\nClick below to join:\n{channel_invite_link}")
    else:
        keyboard = [
            [InlineKeyboardButton(
                "✅ Open Mini-App & Grant Permission",
                web_app=WebAppInfo(url="https://kingcryptocalls.com/miniapp")
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 Open the mini-app to continue.", reply_markup=reply_markup)

# ✅ Handle Button Click (Grant Permission)
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
    except Exception:
        await query.answer("❌ Failed to decode link.")
        return

    allowed_users.add(user_id)
    await query.answer("✅ Permission granted!")
    await query.message.edit_text("✅ You have granted permission!")
    await context.bot.send_message(chat_id=user_id, text=f"🚀 Click below to join the channel:\n{channel_invite_link}")

# ✅ Broadcast Message (Admin Only)
async def broadcast(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)

    # ✅ Only allow admin (6142725643) to broadcast messages
    if user_id != "6142725643":
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

# ✅ Run Bot with Proper Event Loop Handling
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_running():
        logger.warning("⚠️ Event loop already running. Creating new task.")
        loop.create_task(run_bot())
    else:
        asyncio.run(run_bot())  # ✅ Fixes event loop issues
