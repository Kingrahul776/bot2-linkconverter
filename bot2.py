import os
import requests
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

BOT2_TOKEN = os.getenv("BOT2_TOKEN")  # ✅ Token for Bot 2
RAILWAY_APP_URL = "https://web-production-8fdb0.up.railway.app"  # ✅ Backend URL
SUBSCRIBERS_FILE = "subscribers.json"  # ✅ Store user data
ADMIN_ID = 6142725643  # ✅ Your Telegram ID

# ✅ Load Subscribers
def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# ✅ Save Subscribers
def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f)

# ✅ Handle "/start <short_code>"
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username
    args = context.args  # Get the tracking short code

    if not args:
        await update.message.reply_text("❌ Invalid link. Please request a new link.")
        return

    short_code = args[0]

    # ✅ Retrieve the private link from the backend
    response = requests.get(f"{RAILWAY_APP_URL}/get_link?short_code={short_code}")
    result = response.json()

    if not result["success"]:
        await update.message.reply_text("❌ Invalid or expired link.")
        return

    private_link = result["private_link"]

    subscribers = load_subscribers()

    # ✅ Store user permission for broadcasting
    if str(user_id) not in subscribers:
        subscribers[str(user_id)] = {"username": user_name, "short_code": short_code}
        save_subscribers(subscribers)

    # ✅ Ask for permission to send messages
    keyboard = [[InlineKeyboardButton("✅ Allow Messages & Join Channel", url=private_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 Click below to join the channel & allow future messages:",
        reply_markup=reply_markup
    )

# ✅ Admin Command to Broadcast Messages
async def broadcast(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    subscribers = load_subscribers()
    count = 0

    for user_id in subscribers:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            count += 1
        except Exception as e:
            print(f"[ERROR] Failed to send message to {user_id}: {e}")

    await update.message.reply_text(f"✅ Broadcast sent to {count} users.")

# ✅ Main Function
async def run_bot():
    app = Application.builder().token(BOT2_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("🚀 Bot 2 is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(100)

if __name__ == "__main__":
    asyncio.run(run_bot())
