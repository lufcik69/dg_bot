import os
import discord
from discord.ext import commands
from langdetect import detect
import requests

TOKEN = os.getenv("DISCORD_TOKEN")  # Put your Discord bot token in Render's env
BASE_URL = "https://libretranslate.com"
LANGUAGES = {'en': 'English', 'pl': 'Polish', 'ru': 'Russian'}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def translate(text, source_lang, target_lang):
    try:
        response = requests.post(
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
        return response.json().get("translatedText", "[Translation failed]")
    except Exception as e:
        print(f"Translation error: {e}")
        return "[Translation failed]"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    text = message.content

    try:
        detected = detect(text)
    except:
        await message.channel.send("❌ Could not detect language.")
        return

    if detected not in LANGUAGES:
        await message.channel.send("❌ Only English, Polish, and Russian are supported.")
        return

    translations = [
        f"**{LANGUAGES[lang]}**: {translate(text, detected, lang)}"
        for lang in LANGUAGES if lang != detected
    ]

    await message.channel.send("\n".join(translations))

    await bot.process_commands(message)  # Keeps bot commands working if needed
