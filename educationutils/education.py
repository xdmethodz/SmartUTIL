import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# Function to fetch synonyms and antonyms using Datamuse API
def fetch_synonyms_antonyms(word):
    synonyms_response = requests.get(f"https://api.datamuse.com/words?rel_syn={word}")
    antonyms_response = requests.get(f"https://api.datamuse.com/words?rel_ant={word}")

    synonyms = [syn['word'] for syn in synonyms_response.json()]
    antonyms = [ant['word'] for ant in antonyms_response.json()]

    return synonyms, antonyms

# Function to translate text using Global Translator API
def translate_text(text, target_lang):
    response = requests.get(f"https://global-translator-api.bjcoderx.workers.dev/?text={text}&targetLang={target_lang}")
    response_data = response.json()
    translated_text = response_data.get("translatedText", "Translation failed")
    return translated_text

def setup_education_handler(app: Client):
    @app.on_message(filters.command("syn"))
    async def synonyms_handler(client: Client, message: Message):
        if len(message.command) <= 1:
            await message.reply_text("**Please Enter The Word To Get Synonyms And Antonyms**", parse_mode=ParseMode.MARKDOWN)
            return

        word = message.command[1]
        loading_message = await message.reply_text("**Fetching Synonyms and Antonyms...**", parse_mode=ParseMode.MARKDOWN)

        try:
            synonyms, antonyms = fetch_synonyms_antonyms(word)
            synonyms_text = ", ".join(synonyms) if synonyms else "No synonyms found"
            antonyms_text = ", ".join(antonyms) if antonyms else "No antonyms found"

            response_text = (
                f"**Synonyms:**\n{synonyms_text}\n\n"
                f"**Antonyms:**\n{antonyms_text}"
            )

            await loading_message.delete()
            await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await loading_message.delete()
            await message.reply_text(f"**An error occurred: {str(e)}**", parse_mode=ParseMode.MARKDOWN)

    @app.on_message(filters.command("tr"))
    async def translate_handler(client: Client, message: Message):
        if len(message.command) <= 2:
            await message.reply_text("**Please Enter A Language Code and Text To Translate e.g. /tr bn Hello**", parse_mode=ParseMode.MARKDOWN)
            return

        target_lang = message.command[1]
        text_to_translate = " ".join(message.command[2:])
        loading_message = await message.reply_text(f"**Translating Text Into {target_lang} language...**", parse_mode=ParseMode.MARKDOWN)

        try:
            translated_text = translate_text(text_to_translate, target_lang)
            await loading_message.delete()
            await message.reply_text(f"`{translated_text}`", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await loading_message.delete()
            await message.reply_text(f"**An error occurred: {str(e)}**", parse_mode=ParseMode.MARKDOWN)
