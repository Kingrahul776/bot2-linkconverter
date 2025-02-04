import logging
import asyncio
import jwt  # ✅ Import JWT for decoding links
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# ✅ Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot Token & Admin ID
BOT2_TOKEN = "7907835521:AAE6FP3yU-aoKYXXEX05kio4SV3j1IJACyc"
SECRET_KEY = "supersecret"  # ✅ Must be the same as Web API
ADMIN_ID = 6142725643  # ✅ Admin ID

# ✅ Initialize Bot
app = Application.builder().token(BOT2_TOKEN).build()

# ✅ Store Users Who Granted Permission
allowed_users = set()

# ✅ Start Command (Handles Redirection)
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

    if user_id in allowed_users:
        await update.message.reply_text(f"🚀 You have already granted permission!\nClick below to join:\n{channel_invite_link}")
    else:
        keyboard = [[InlineKeyboardButton("✅ Grant Permission", callback_data=f"grant_access:{args[0]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 Welcome! Grant permission to continue.", reply_markup=reply_markup)

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

# ✅ Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_click))

# ✅ Fix Event Loop Issues
async def run_bot():
    logger.info("🚀 Bot 2 is starting...")
    await app.initialize()
    await app.run_polling()

if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        logger.warning("⚠️ Event loop already running. Running bot in a new task.")
        loop.create_task(run_bot())
    else:
        asyncio.run(run_bot())  # ✅ Runs properly if no loop is running
