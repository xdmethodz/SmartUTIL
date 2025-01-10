import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# Function to fetch GPT response from the API
def fetch_gpt_response(prompt, model):
    url = f"https://darkness.ashlynn.workers.dev/chat/?prompt={prompt}&model={model}"
    response = requests.get(url)
    response_data = response.json()
    return response_data.get('response', None)

def setup_gpt_handlers(app: Client):
    @app.on_message(filters.command("gpt4") & filters.private)
    async def gpt4_handler(client, message):
        await message.reply_text("**GPT-4 Gate Off 🔕**", parse_mode=ParseMode.MARKDOWN)

    @app.on_message(filters.command("gpt") & filters.private)
    async def gpt_handler(client, message):
        try:
            # Check if a prompt is provided
            if len(message.command) <= 1:
                await message.reply_text("**Please provide a prompt for GPT response**", parse_mode=ParseMode.MARKDOWN)
                return

            prompt = " ".join(message.command[1:])
            # Fetch response from the API
            response_text = fetch_gpt_response(prompt, "gpt-4o-mini")
            if response_text:
                # Send the response text to the user
                await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
            else:
                await message.reply_text("**Error Generating Response...**", parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await message.reply_text("**Error Generating Response...**", parse_mode=ParseMode.MARKDOWN)

# To use the handler, call setup_gpt_handlers(app) in your main script
