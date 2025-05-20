import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langdetect import detect

# Logging setup
logging.basicConfig(level=logging.INFO)

# Env variables
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app-name.onrender.com

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # ✅ This starts the webhook properly
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )
from aiohttp import web

async def health_check(request):
    return web.Response(text="Bot is alive!")

app.web_app.add_routes([web.get("/", health_check)])
