import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langdetect import detect
from deep_translator import GoogleTranslator

# Logging setup
logging.basicConfig(level=logging.INFO)

# Read token from environment variable
TOKEN = os.getenv("TOKEN")

# Languages map
lang_map = {
    'en': 'English',
    'pl': 'Polish',
    'ru': 'Russian'
}

# Translate function using Deep Translator
def translate_text(text, source_lang, target_lang):
    try:
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return "[Translation failed]"

# Main handler
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    logging.info(f"Received message: {original_text}")

    try:
        detected_lang = detect(original_text)
        logging.info(f"Detected language: {detected_lang}")
    except Exception as e:
        await update.message.reply_text("Language detection failed.")
        return

    if detected_lang not in lang_map:
        await update.message.reply_text("Only English, Polish, and Russian are supported.")
        return

    translations = []
    for lang_code in ['en', 'pl', 'ru']:
        if lang_code != detected_lang:
            translated = translate_text(original_text, detected_lang, lang_code)
            translations.append(f"{lang_map[lang_code]}: {translated}")

    await update.message.reply_text("\n".join(translations))

# App entry point
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_message))
    app.run_polling()
