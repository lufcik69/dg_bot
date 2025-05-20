import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langdetect import detect

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load Telegram token from environment
TOKEN = os.getenv("TOKEN")

# Languages we're supporting
LANGUAGES = {
    'en': 'English',
    'pl': 'Polish',
    'ru': 'Russian'
}

# ✅ Official public LibreTranslate API endpoint
BASE_URL = "https://libretranslate.com"

def translate(text, source_lang, target_lang):
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            json={
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return result.get("translatedText", "[Translation failed]")
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "[Translation failed]"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        detected_lang = detect(text)
        logging.info(f"Detected language: {detected_lang}")
    except Exception:
        await update.message.reply_text("Could not detect language.")
        return

    if detected_lang not in LANGUAGES:
        await update.message.reply_text("Only English, Polish, and Russian are supported.")
        return

    translations = []
    for lang_code in LANGUAGES:
        if lang_code != detected_lang:
            translated = translate(text, detected_lang, lang_code)
            translations.append(f"{LANGUAGES[lang_code]}: {translated}")

    await update.message.reply_text("\n".join(translations))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
