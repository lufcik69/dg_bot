import os
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram import Update
from langdetect import detect
import requests
import logging

# Logging
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Full URL e.g. https://your-app.onrender.com/webhook

LANGUAGES = {
    'en': 'English',
    'pl': 'Polish',
    'ru': 'Russian'
}

BASE_URL = "https://libretranslate.com"

def translate(text, source_lang, target_lang):
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            json={"q": text, "source": source_lang, "target": target_lang, "format": "text"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.json().get("translatedText", "[Translation failed]")
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "[Translation failed]"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        detected_lang = detect(text)
    except:
        await update.message.reply_text("Could not detect language.")
        return

    if detected_lang not in LANGUAGES:
        await update.message.reply_text("Only English, Polish, and Russian are supported.")
        return

    translations = [
        f"{LANGUAGES[lang]}: {translate(text, detected_lang, lang)}"
        for lang in LANGUAGES if lang != detected_lang
    ]

    await update.message.reply_text("\n".join(translations))

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Start webhook instead of polling
    await app.start()
    await app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
