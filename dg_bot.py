import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from langdetect import detect
from deep_translator import GoogleTranslator

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Replace with your own bot token
TOKEN = "7493784409:AAEFXLxPQeE97wA6v337Xz-sh2EgmOI42Kc"

# Function to handle messages
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text

    try:
        source_lang = detect(original_text)
    except:
        await update.message.reply_text("Sorry, I couldn't detect the language.")
        return

    lang_map = {
        'en': 'English',
        'pl': 'Polish',
        'ru': 'Russian'
    }

    if source_lang not in lang_map:
        await update.message.reply_text("Only Polish, Russian, and English are supported.")
        return

    translations = []
    for lang_code in ['en', 'pl', 'ru']:
        if lang_code != source_lang:
            try:
                translated = GoogleTranslator(source=source_lang, target=lang_code).translate(original_text)
                translations.append(f"{lang_map[lang_code]}: {translated}")
            except:
                translations.append(f"{lang_map[lang_code]}: [Translation failed]")

    response = "\n".join(translations)
    await update.message.reply_text(response)

# Main function to start the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), translate_message))

    print("Bot is running...")
    app.run_polling()
