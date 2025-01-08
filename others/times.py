import pytz
import pycountry
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

def get_time_for_country(country_code):
    # Get the country name and flag emoji
    country = pycountry.countries.get(alpha_2=country_code)
    if not country:
        raise ValueError("Invalid country code")

    country_name = country.name
    flag_emoji = chr(0x1F1E6 + ord(country_code[0]) - ord('A')) + chr(0x1F1E6 + ord(country_code[1]) - ord('A'))

    # Get the time zone for the country
    time_zone = pytz.country_timezones.get(country_code)
    if not time_zone:
        raise ValueError("No time zone found for this country")

    tz = pytz.timezone(time_zone[0])
    now = datetime.now(tz)

    # Format the time and date
    time_str = now.strftime("%I:%M:%S %p")
    date_str = now.strftime("%Y-%m-%d")
    day_str = now.strftime("%A")

    return f"{flag_emoji} <b>{country_name}:</b> Current Time & Date\n━━━━━━━━━━━━━━━━━\n🕰️ <b>Time:</b> <code>{time_str}</code>\n📆 <b>Date:</b> <code>{date_str}</code>\n📅 <b>Day:</b> <code>{day_str}</code>"

def setup_time_handler(app: Client):
    @app.on_message(filters.command("time") & filters.private)
    async def handle_time_command(client, message):
        if len(message.command) == 1:
            await message.reply_text(
                "<b>Ensure you provided a valid country code.</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            country_code = message.command[1].upper()
            try:
                result = get_time_for_country(country_code)
                await message.reply_text(result, parse_mode=ParseMode.HTML)
            except Exception as e:
                await message.reply_text(
                    f"<b>Error:</b> {str(e)}",
                    parse_mode=ParseMode.HTML
                )