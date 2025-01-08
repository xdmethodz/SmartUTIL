import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, 
    SessionPasswordNeeded, PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError, 
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError
)
from asyncio.exceptions import TimeoutError

# Constants for timeouts
TIMEOUT_OTP = 600  # 10 minutes
TIMEOUT_2FA = 300  # 5 minutes

sessions = {}

def setup_string_handler(app: Client):
    @app.on_message(filters.command("pyro") & filters.private)
    async def pyro_command(client, message):
        await start_session(client, message, telethon=False)

    @app.on_message(filters.command("tele") & filters.private)
    async def tele_command(client, message):
        await start_session(client, message, telethon=True)

    async def start_session(client, message, telethon=False):
        session_type = "Telethon" if telethon else "Pyrogram"
        sessions[message.chat.id] = {"type": session_type, "stage": "start"}
        await message.reply(
            f"**Welcome to the {session_type} session setup!**\n"
            "**━━━━━━━━━━━━━━━━━**\n"
            "**This is a totally safe session string generator. We don't save any info that you will provide, so this is completely safe.**\n\n"
            "**Note: Don't send OTP directly. Otherwise, your account could be banned, or you may not be able to log in.**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Start", callback_data=f"start_{session_type.lower()}"),
                 InlineKeyboardButton("Close", callback_data="close")]
            ])
        )

    @app.on_callback_query(filters.regex(r"^start_(pyrogram|telethon)"))
    async def on_start_callback(client, callback_query):
        session_type = callback_query.data.split('_')[1]
        sessions[callback_query.message.chat.id]["stage"] = "api_id"
        await callback_query.message.edit_text(
            "<b>Send Your API ID</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Restart", callback_data=f"restart_{session_type}"),
                 InlineKeyboardButton("Close", callback_data="close")]
            ]),
            parse_mode=ParseMode.HTML
        )

    @app.on_callback_query(filters.regex(r"^restart_(pyrogram|telethon)"))
    async def on_restart_callback(client, callback_query):
        session_type = callback_query.data.split('_')[1]
        await start_session(client, callback_query.message, telethon=(session_type == "telethon"))

    @app.on_callback_query(filters.regex(r"^close"))
    async def on_close_callback(client, callback_query):
        chat_id = callback_query.message.chat.id
        sessions.pop(chat_id, None)  # Remove session if exists
        await callback_query.message.edit_text("Session generation process has been closed.")

    @app.on_message(filters.text & filters.private)
    async def on_text_message(client, message):
        chat_id = message.chat.id
        if chat_id not in sessions:
            return

        session = sessions[chat_id]
        stage = session.get("stage")

        if await cancelled(message):
            sessions.pop(chat_id, None)
            return

        if stage == "api_id":
            try:
                api_id = int(message.text)
                session["api_id"] = api_id
                session["stage"] = "api_hash"
                await message.reply(
                    "<b>Send Your API Hash</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                         InlineKeyboardButton("Close", callback_data="close")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            except ValueError:
                await message.reply("Invalid API ID. Please enter a valid integer.")

        elif stage == "api_hash":
            session["api_hash"] = message.text
            session["stage"] = "phone_number"
            await message.reply(
                "<b>Send Your Phone Number\n[Example: +880xxxxxxxxxx]</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ]),
                parse_mode=ParseMode.HTML
            )

        elif stage == "phone_number":
            session["phone_number"] = message.text
            await message.reply("Sending OTP...")
            await send_otp(client, message)

        elif stage == "otp":
            otp = ''.join(filter(str.isdigit, message.text))
            session["otp"] = otp
            await message.reply("Validating OTP...")
            await validate_otp(client, message)

        elif stage == "2fa":
            session["password"] = message.text
            await validate_2fa(client, message)

    async def send_otp(client, message):
        session = sessions[message.chat.id]
        api_id, api_hash, phone_number = session["api_id"], session["api_hash"], session["phone_number"]
        telethon = session["type"] == "Telethon"

        client_obj = TelegramClient(StringSession(), api_id, api_hash) if telethon else Client(
            in_memory=True, api_id=api_id, api_hash=api_hash
        )
        await client_obj.connect()

        try:
            code = await client_obj.send_code_request(phone_number) if telethon else await client_obj.send_code(phone_number)
            session.update({"client_obj": client_obj, "code": code, "stage": "otp"})
            await message.reply(
                "<b>Send The OTP as text. Example: 'AB1 CD2 EF3 GH4 IJ5'</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ]),
                parse_mode=ParseMode.HTML
            )
        except (ApiIdInvalid, ApiIdInvalidError):
            await message.reply(
                '`API_ID` and `API_HASH` combination is invalid. Please restart.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
            await client_obj.disconnect()
        except (PhoneNumberInvalid, PhoneNumberInvalidError):
            await message.reply(
                '`PHONE_NUMBER` is invalid. Please restart.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
            await client_obj.disconnect()

    async def validate_otp(client, message):
        session = sessions[message.chat.id]
        client_obj, phone_number, otp = session["client_obj"], session["phone_number"], session["otp"]
        telethon = session["type"] == "Telethon"

        try:
            if telethon:
                await client_obj.sign_in(phone_number, otp)
            else:
                await client_obj.sign_in(phone_number, session["code"].phone_code_hash, otp)
            await generate_session(client, message)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            await message.reply(
                'OTP is invalid. Please restart.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            await message.reply(
                'OTP has expired. Please restart.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ])
            )
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            session["stage"] = "2fa"
            await message.reply(
                "<b>2FA is required. Please enter your password.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ]),
                parse_mode=ParseMode.HTML
            )

    async def validate_2fa(client, message):
        session = sessions[message.chat.id]
        client_obj, password = session["client_obj"], session["password"]

        try:
            await client_obj.sign_in(password=password) if session["type"] == "Telethon" else await client_obj.check_password(password=password)
            await generate_session(client, message)
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await message.reply(
                'Invalid 2FA password. Please restart.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Restart", callback_data=f"restart_{session['type'].lower()}"),
                     InlineKeyboardButton("Close", callback_data="close")]
                ])
            )

    async def generate_session(client, message):
        session = sessions[message.chat.id]
        client_obj = session["client_obj"]
        telethon = session["type"] == "Telethon"

        try:
            string_session = client_obj.session.save() if telethon else await client_obj.export_session_string()
            await client_obj.send_message("me", f"**{session['type'].upper()} SESSION**:\n\n`{string_session}`")
        except Exception:
            await message.reply("Failed to send session to saved messages.")

        await client_obj.disconnect()
        await message.reply(
            "<b>Your session string has been saved to your Saved Messages.</b>",
            parse_mode=ParseMode.HTML
        )
        del sessions[message.chat.id]

    async def cancelled(message):
        if message.text in ["/cancel", "/restart"] or message.text.startswith("/"):
            await message.reply("Cancelled the process." if "/cancel" in message.text else "Restarted the process.", quote=True)
            return True
        return False
