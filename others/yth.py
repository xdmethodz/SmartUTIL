from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import re

def youtube_parser(url):
    # Regular expression to extract YouTube video ID from URL
    reg_exp = r"^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
    match = re.match(reg_exp, url)
    return match.group(7) if match and len(match.group(7)) == 11 else False

def setup_yth_handler(app: Client):
    @app.on_message(filters.command("yth") & filters.private)
    async def handle_yth_command(client, message):
        if len(message.command) == 1:
            await message.reply_text(
                "<b>Provide a Valid YouTube link</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            youtube_url = message.command[1]
            video_id = youtube_parser(youtube_url)
            if not video_id:
                await message.reply_text(
                    "<b>Invalid YouTube link</b>",
                    parse_mode=ParseMode.HTML
                )
                return
            
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            caption = "<code>Photo Send By ➤ @abir_x_official_developer</code>"
            
            await client.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail_url,
                caption=caption,
                parse_mode=ParseMode.HTML
            )

# To use the handler, you would call setup_yth_handler(app) in your main script