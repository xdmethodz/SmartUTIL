from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import base64
import binascii

def setup_decoders_handler(app: Client):
    commands = {
        "b64en": lambda text: base64.b64encode(text.encode()).decode(),
        "b64de": lambda text: base64.b64decode(text).decode(),
        "b32en": lambda text: base64.b32encode(text.encode()).decode(),
        "b32de": lambda text: base64.b32decode(text).decode(),
        "binen": lambda text: ' '.join(format(ord(char), '08b') for char in text),
        "binde": lambda text: ''.join(chr(int(b, 2)) for b in text.split()),
        "hexen": lambda text: binascii.hexlify(text.encode()).decode(),
        "hexde": lambda text: binascii.unhexlify(text).decode(),
        "octen": lambda text: ' '.join(format(ord(char), '03o') for char in text),
        "octde": lambda text: ''.join(chr(int(o, 8)) for o in text.split()),
        "trev": lambda text: text[::-1],
        "tcap": lambda text: text.upper(),
        "tsm": lambda text: text.lower(),
        "wc": lambda text: f"<b>Text Counter</b>\n\n<b>Words:</b> <code>{len(text.split())}</code>\n<b>Characters:</b> <code>{len(text)}</code>\n<b>Sentences:</b> <code>{text.count('.') + text.count('!') + text.count('?')}</code>\n<b>Paragraphs:</b> <code>{text.count('\n') + 1}</code>"
    }

    for command, func in commands.items():
        @app.on_message(filters.command(command) & filters.private)
        async def handle_command(client, message, func=func, command=command):
            if len(message.command) == 1 and not message.reply_to_message:
                await message.reply_text(
                    f"<b>Please provide a text or reply to a message to {'encode' if 'en' in command else 'decode' if 'de' in command else 'transform'} by {command}</b>",
                    parse_mode=ParseMode.HTML
                )
            else:
                text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
                try:
                    result = func(text)
                    await message.reply_text(
                        f"<b>{command} {'encoded' if 'en' in command else 'decoded' if 'de' in command else 'transformed'}:</b>\n<code>{result}</code>" if command != "wc" else result,
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    await message.reply_text(
                        f"<b>Error:</b> {str(e)}",
                        parse_mode=ParseMode.HTML
                    )