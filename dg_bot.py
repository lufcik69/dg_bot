import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, filters
)
from langdetect import detect
import asyncio

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Environment Variables
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-bot-name.onrender.com
PORT = int(os.getenv("PORT", 8000))

logging.info(f"Using PORT: {PORT}")
logging.info(f"Using WEBHOOK_URL: {WEBHOOK_URL}")

# Language config
LANGUAGES = {'en': 'English', 'pl': 'Polish', 'ru': 'Russian'}
BASE_URL = "https://libretranslate.com"

# Translation function
def translate(text, source_lang, target_lang):
    try:
        res = requests.post(
            f"{BASE_URL}/translate",
            json={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return res.json().get("translatedText", "[Translation failed]")
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "[Translation failed]"

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        detected = detect(text)
    except:
        await update.message.reply_text("Could not detect language.")
        return

    if detected not in LANGUAGES:
        await update.message.reply_text("Only English, Polish, and Russian are supported.")
        return

    translations = [
        f"{LANGUAGES[lang]}: {translate(text, detected, lang)}"
        for lang in LANGUAGES if lang != detected
    ]
    await update.message.reply_text("\n".join(translations))

# Main bot startup
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.initialize()
    await application.start()

    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

    logging.info("✅ Webhook started and listening.")
    await application.updater.idle()
    logging.info("⏹️ Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
