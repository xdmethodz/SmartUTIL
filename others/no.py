from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# List of commands to handle
COMMANDS = [
    "gem", "imgai", "gen", "bin", "scr", "fcc", "extp", "mgen", "mc", "topbin",
    "binbank", "bindb", "adbin", "rmbin", "p2p", "fb", "pin", "in", "sp", 
    "video", "song", "spell", "gra", "prn", "fmail", "fpass", "scrmail", 
    "pyro", "tele", "ss", "ws"
]

# Function to handle commands
async def handle_command(client: Client, message: Message):
    await message.reply_text("**Hey Bro Sorry This Feature Has Not Been Added🙂**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

# Function to set up handlers for each command
def setup_no_handlers(app: Client):
    for command in COMMANDS:
        app.add_handler(filters.command(command) & filters.private, handle_command)
