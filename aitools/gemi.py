import os
import io
import logging
from PIL import Image
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
import google.generativeai as genai

# Google Api Key
GOOGLE_API_KEY = "AIzaSyCqSQmOL7XPlhCXrj_A6RkDI7JupBKZ58g"  # Replace this with your Google API Key
MODEL_NAME = "gemini-1.5-flash"  # Don't change this model

# Configure the API key
genai.configure(api_key=GOOGLE_API_KEY)

def setup_gemi_handlers(app: Client):
    @app.on_message(filters.command("gem") & filters.private)
    async def gemi_handler(client: Client, message: Message):
        loading_message = None
        try:
            loading_message = await message.reply_text("**Generating response, please wait...**", parse_mode=ParseMode.MARKDOWN)

            if len(message.text.strip()) <= 5:
                await message.reply_text("**Provide a prompt after the command.**", parse_mode=ParseMode.MARKDOWN)
                return

            prompt = message.text.split(maxsplit=1)[1]
            response = genai.generate_content(model=MODEL_NAME, prompt=prompt)

            response_text = response['text']
            if len(response_text) > 4000:
                parts = [response_text[i:i + 4000] for i in range(0, len(response_text), 4000)]
                for part in parts:
                    await message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
            else:
                await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            await message.reply_text("**An error occurred: Please try again.**", parse_mode=ParseMode.MARKDOWN)
        finally:
            if loading_message:
                await loading_message.delete()

    @app.on_message(filters.command("imgai") & filters.private)
    async def generate_from_image(client: Client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply_text("**Please reply to a photo for a response.**", parse_mode=ParseMode.MARKDOWN)
            return

        prompt = message.command[1] if len(message.command) > 1 else message.reply_to_message.caption or "Describe this image."

        processing_message = await message.reply_text("**Generating response, please wait...**", parse_mode=ParseMode.MARKDOWN)

        try:
            img_data = await client.download_media(message.reply_to_message, in_memory=True)
            img = Image.open(io.BytesIO(img_data.getbuffer()))

            response = genai.generate_content(model=MODEL_NAME, prompt=[prompt, img])
            response_text = response['text']

            await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Error during image analysis: {e}")
            await message.reply_text("**An error occurred. Please try again.**", parse_mode=ParseMode.MARKDOWN)
        finally:
            await processing_message.delete()

# To use the handler, call setup_gemi_handlers(app) in your main script
