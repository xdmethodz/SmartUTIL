from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied, ChannelInvalid

def setup_info_handler(app: Client):
    @app.on_message(filters.command("info") & filters.private)
    async def handle_info_command(client, message):
        if len(message.command) == 1:
            # No username or chat provided, show current user info
            user = message.from_user
            response = (
                f"🌟 <b>Full Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
                f"🔖 <b>Username:</b> <code>@{user.username}</code>\n"
                f"💬 <b>Chat Id:</b> <code>{user.id}</code>"
            )
            await message.reply_text(response, parse_mode=ParseMode.HTML)
        else:
            username = message.command[1].strip('@')
            try:
                # Attempt to fetch public user or bot info
                user = await client.get_users([username])
                user = user[0]
                response = (
                    f"🌟 <b>Full Name:</b> <code>{user.first_name} {user.last_name or ''}</code>\n"
                    f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
                    f"🔖 <b>Username:</b> <code>@{user.username}</code>\n"
                    f"💬 <b>Chat Id:</b> <code>{user.id}</code>"
                )
                await message.reply_text(response, parse_mode=ParseMode.HTML)
            except (PeerIdInvalid, UsernameNotOccupied):
                try:
                    # Attempt to fetch public group/channel info
                    chat = await client.get_chat(username)
                    if chat.username:  # Check if it's public
                        if chat.type == "channel":
                            response = (
                                f"📛 <b>{chat.title}</b>\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
                                f"📌 <b>Type:</b> <code>Channel</code>\n"
                                f"👥 <b>Member count:</b> <code>{chat.members_count or 'Unknown'}</code>"
                            )
                        elif chat.type in ["supergroup", "group"]:
                            response = (
                                f"📛 <b>{chat.title}</b>\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
                                f"📌 <b>Type:</b> <code>{'Supergroup' if chat.type == 'supergroup' else 'Group'}</code>\n"
                                f"👥 <b>Member count:</b> <code>{chat.members_count or 'Unknown'}</code>"
                            )
                        else:
                            response = "<b>Invalid chat type</b>"
                        await message.reply_text(response, parse_mode=ParseMode.HTML)
                    else:
                        await message.reply_text(
                            "<b>Chat is private. Add the bot to the group/channel to fetch info.</b>",
                            parse_mode=ParseMode.HTML
                        )
                except (ChannelInvalid, PeerIdInvalid):
                    await message.reply_text(
                        "<b>Invalid username or chat not found</b>",
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    await message.reply_text(f"<b>Error:</b> {str(e)}", parse_mode=ParseMode.HTML)
