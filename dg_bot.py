import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langdetect import detect

# Logging
logging.basicConfig(level=logging.INFO)

# Get Telegram Bot Token from environment
TOKEN = os.getenv("7493784409:AAEFXLxPQeE97wA6v337Xz-sh2EgmOI42Kc")

# LibreTranslate API (you can self-host or use their public instance)
TRANSLATE_API = "https://libretranslate.com/translate"

# Supported languages
lang_map = {
    'en': 'English',
    'pl': 'Polish',
    'ru': 'Russian'
}

# Translate using LibreTranslate API
def translate(text, source_lang, target_lang):
    try:
        response = requests.post(
            TRANSLATE_API,
            data={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("translatedText", "[Translation failed]")
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "[Translation error]"

# Telegram message handler
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    logging.info(f"Received: {original_text}")

    try:
        source_lang = detect(original_text)
    except Exception as e:
        logging.warning(f"Language detection failed: {e}")
        await update.message.reply_text("Could not detect language.")
        return

    if source_lang not in lang_map:
        await update.message.reply_text("Only English, Polish, and Russian are supported.")
        return

    translations = []
    for target_lang in ['en', 'pl', 'ru']:
        if target_lang != source_lang:
            translated = translate(original_text, source_lang, target_lang)
            translations.append(f"{lang_map[target_lang]}: {translated}")

    await update.message.reply_text("\n".join(translations))

# Start the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_message))
    app.run_polling()
