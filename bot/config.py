import os


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError(
        "Missing bot token. Set the TELEGRAM_BOT_TOKEN environment variable."
    )
