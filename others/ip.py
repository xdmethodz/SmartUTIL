import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

def get_ip_info(ip: str) -> str:
    url = f"https://ipinfo.io/{ip}/json"
    response = requests.get(url)

    if response.status_code != 200:
        return "Invalid IP address"

    data = response.json()
    ip = data.get("ip", "Unknown")
    asn = data.get("org", "Unknown")
    isp = data.get("org", "Unknown")
    country = data.get("country", "Unknown")
    city = data.get("city", "Unknown")
    timezone = data.get("timezone", "Unknown")

    # Simulated IP fraud score and risk level for demonstration
    fraud_score = 0
    risk_level = "low" if fraud_score < 50 else "high"

    details = (
        f"YOUR IP INFORMATION 🌐\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"**IP:** `{ip}`\n"
        f"**ASN:** `{asn}`\n"
        f"**ISP:** `{isp}`\n"
        f"**Country City:** `{country} {city}`\n"
        f"**Timezone:** `{timezone}`\n"
        f"**IP Fraud Score:** `{fraud_score}`\n"
        f"**Risk LEVEL:** `{risk_level} Risk`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

    return details

async def ip_info_handler(client: Client, message: Message):
    if len(message.command) <= 1:
        await message.reply_text("**❌ Please provide a single IP address.**", parse_mode=ParseMode.MARKDOWN)
        return

    ip = message.command[1]
    details = get_ip_info(ip)

    user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_profile_link = f"https://t.me/{message.from_user.username}"

    details += f"**Ip-Info Grab By:** [{user_full_name}]({user_profile_link})"

    await message.reply_text(details, parse_mode=ParseMode.MARKDOWN)

def setup_ip_handlers(app: Client):
    @app.on_message(filters.command("ip") & filters.private)
    async def ip_info(client: Client, message: Message):
        await ip_info_handler(client, message)

# To use the handler, call setup_ip_handlers(app) in your main script
