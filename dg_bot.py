import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langdetect import detect

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")  # Get your bot token from Render environment variables

LANGUAGES = {
    'en': 'English',
    'pl': 'Polish',
    'ru': 'Russian'
}

TRANSLATE_URL = "https://libretranslate.com/translate"

def translate(text, source_lang, target_lang):
    try:
        response = requests.post(TRANSLATE_URL, data={
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }, timeout=5)

        result = response.json()
        return result['translatedText']
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "[Translation failed]"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    logging.info(f"Received message: {message}")

    try:
        detected_lang = detect(message)
    except Exception:
        await update.message.reply_text("Could not detect language.")
        return

    if detected_lang not in LANGUAGES:
        await update.message.reply_text("Supported languages: English, Polish, Russian.")
        return

    translations = []
    for lang_code in LANGUAGES:
        if lang_code != detected_lang:
            translated = translate(message, detected_lang, lang_code)
            translations.append(f"{LANGUAGES[lang_code]}: {translated}")

    reply = "\n".join(translations)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
