import os

# ✅ Print all environment variables (for debugging)
print("🚀 Available Environment Variables in Railway:")
print(os.environ)

# ✅ Check if BOT2_TOKEN is set
BOT2_TOKEN = os.getenv("BOT2_TOKEN")

if not BOT2_TOKEN:
    raise ValueError("🚨 ERROR: BOT2_TOKEN is missing! Set it in Railway.")

print(f"✅ BOT2_TOKEN Loaded: {BOT2_TOKEN[:5]}********")
