import os

# ✅ Debug: Print available Railway environment variables
print("🚀 Checking environment variables in Railway...")
print(os.environ)

# ✅ Manually try to fetch BOT2_TOKEN
BOT2_TOKEN = os.getenv("BOT2_TOKEN")

if not BOT2_TOKEN:
    print("🚨 ERROR: BOT2_TOKEN is missing! Trying alternative method...")
    BOT2_TOKEN = os.popen("printenv BOT2_TOKEN").read().strip()

if not BOT2_TOKEN:
    raise ValueError("🚨 ERROR: BOT2_TOKEN is STILL missing! Set it in Railway.")

print(f"✅ BOT2_TOKEN Loaded: {BOT2_TOKEN[:5]}********")
