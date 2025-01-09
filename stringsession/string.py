import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from asyncio.exceptions import TimeoutError

# Constants for timeouts
TIMEOUT_OTP = 600  # 10 minutes
TIMEOUT_2FA = 300  # 5 minutes

sessions = {}

def setup_string_handler(app: Client):
    @app.on_message(filters.command("pyro") & filters.private)
    async def pyro_command(client, message):
        await proceed_session(client, message, telethon=False)

    @app.on_message(filters.command("tele") & filters.private)
    async def tele_command(client, message):
        await proceed_session(client, message, telethon=True)

    async def proceed_session(client, message, telethon=False):
        session_type = "Telethon" if telethon else "Pyrogram"
        sessions[message.chat.id] = {"type": session_type}
        await message.reply(
            f"**Welcome to the {session_type} session setup!**\n"
            "**━━━━━━━━━━━━━━━━━**\n"
            "**This is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.**\n\n"
            "**Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Proceed", callback_data=f"proceed_{session_type.lower()}"),
                InlineKeyboardButton("Close", callback_data="close")
            ]])
        )

    @app.on_callback_query(filters.regex(r"^proceed_(pyrogram|telethon)"))
    async def on_proceed_callback(client, callback_query):
        session_type = callback_query.data.split('_')[1]
        await callback_query.message.edit_text(
            "<b>Send Your API ID</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Retry", callback_data=f"retry_{session_type}"),
                InlineKeyboardButton("Close", callback_data="close")
            ]]),
            parse_mode=ParseMode.HTML
        )
        sessions[callback_query.message.chat.id]["stage"] = "api_id"

    @app.on_callback_query(filters.regex(r"^retry_(pyrogram|telethon)"))
    async def on_retry_callback(client, callback_query):
        session_type = callback_query.data.split('_')[1]
        await proceed_session(client, callback_query.message, telethon=(session_type == "telethon"))

    @app.on_callback_query(filters.regex(r"^close"))
    async def on_close_callback(client, callback_query):
        await callback_query.message.edit_text("Session generation process has been closed.")

    @app.on_message(filters.text & filters.private)
    async def on_text_message(client, message):
        chat_id = message.chat.id
        if chat_id not in sessions:
            return

        session = sessions[chat_id]
        stage = session.get("stage")

        if stage == "api_id":
            try:
                api_id = int(message.text)
                session["api_id"] = api_id
                await message.reply(
                    "<b>Send Your API Hash</b>",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"),
                        InlineKeyboardButton("Close", callback_data="close")
                    ]]),
                    parse_mode=ParseMode.HTML
                )
                session["stage"] = "api_hash"
            except ValueError:
                await message.reply("Invalid API ID. Please enter a valid integer.")

        elif stage == "api_hash":
            session["api_hash"] = message.text
            await message.reply(
                "<b>Send Your Phone Number\n[Example: +880xxxxxxxxxx]</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="close")
                ]]),
                parse_mode=ParseMode.HTML
            )
            session["stage"] = "phone_number"

        elif stage == "phone_number":
            session["phone_number"] = message.text
            await message.reply("Sending OTP.....")
            await send_otp(client, message)

        elif stage == "otp":
            otp = ''.join([char for char in message.text if char.isdigit()])
            session["otp"] = otp
            await message.reply("Validating OTP.....")
            await validate_otp(client, message)

        elif stage == "2fa":
            session["password"] = message.text
            await validate_2fa(client, message)

    async def send_otp(client, message):
        session = sessions[message.chat.id]
        api_id = session["api_id"]
        api_hash = session["api_hash"]
        phone_number = session["phone_number"]
        telethon = session["type"] == "Telethon"

        if telethon:
            client_obj = TelegramClient(StringSession(), api_id, api_hash)
        else:
            client_obj = Client(in_memory=True, api_id=api_id, api_hash=api_hash)

        await client_obj.connect()

        try:
            if telethon:
                code = await client_obj.send_code_request(phone_number)
            else:
                code = await client_obj.send_code(phone_number)
            session["client_obj"] = client_obj
            session["code"] = code
            session["stage"] = "otp"
            await message.reply(
                "<b>Send The OTP as text. Please send a text message embedding the OTP like: 'AB1 CD2 EF3 GH4 IJ5'</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="close")
                ]]),
                parse_mode=ParseMode.HTML
            )
        except (ApiIdInvalid, ApiIdInvalidError):
            await message.reply('API_ID and API_HASH combination is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return
        except (PhoneNumberInvalid, PhoneNumberInvalidError):
            await message.reply('PHONE_NUMBER is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return

    async def validate_otp(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        phone_number = session["phone_number"]
        otp = session["otp"]
        code = session["code"]
        telethon = session["type"] == "Telethon"

        try:
            if telethon:
                await client_obj.sign_in(phone_number, otp, password=None)
            else:
                await client_obj.sign_in(phone_number, code.phone_code_hash, otp)
            await generate_session(client, message)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            await message.reply('OTP is invalid. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            await message.reply('OTP is expired. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            session["stage"] = "2fa"
            await message.reply(
                "<b>2FA Is Required To Login. Please Enter 2FA</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"),
                    InlineKeyboardButton("Close", callback_data="close")
                ]]),
                parse_mode=ParseMode.HTML
            )

    async def validate_2fa(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        password = session["password"]
        telethon = session["type"] == "Telethon"

        try:
            if telethon:
                await client_obj.sign_in(password=password)
            else:
                await client_obj.check_password(password=password)
            await generate_session(client, message)
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await message.reply('Invalid Password Provided. Please start generating session again.', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Retry", callback_data=f"retry_{session['type'].lower()}"), InlineKeyboardButton("Close", callback_data="close")]
            ]))
            return

    async def generate_session(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        telethon = session["type"] == "Telethon"

        if telethon:
            string_session = client_obj.session.save()
        else:
            string_session = await client_obj.export_session_string()

        text = f"**{session['type'].upper()} SESSION FROM Smart Nexus**:\n\n{string_session}"

        try:
            await client_obj.send_message("me", text)
        except KeyError:
            pass

        await client_obj.disconnect()
        await message.reply("<b>This string has been saved ✅ in your Saved Messages</b>", parse_mode=ParseMode.HTML)
        del sessions[message.chat.id]

    async def cancelled(message):
        if "/cancel" in message.text:
            await message.reply("Cancelled the Process!", quote=True)
            return True
        elif "/retry" in message.text:
            await message.reply("Restarted the Bot!", quote=True)
            return True
        elif message.text.startswith("/"):  # Bot Commands
            await message.reply("Cancelled the process!", quote=True)
            return True
        else:
            return False
