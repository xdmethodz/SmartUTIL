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
        f"**YOUR IP INFORMATION 🌐**\n"
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

def get_domain_info(domain: str) -> str:
    # Remove the URL scheme (e.g., http://, https://) from the domain if present
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('//')[1]

    url = f"https://api.whois.vu/?q={domain}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Invalid domain name: {domain}"

    data = response.json()
    if "data" not in data or not data["data"]:
        return f"Invalid domain name: {domain}"

    domain_info = data["data"]
    domain_name = domain_info.get("domain_name", "Unknown")
    registrar = domain_info.get("registrar", "Unknown")
    registration = domain_info.get("creation_date", "Unknown")
    expiration = domain_info.get("expiry_date", "Unknown")
    domain_available = "❌" if "registered" in domain_info.get("status", "") else "✅"

    details = (
        f"**Domain:** `{domain_name}`\n"
        f"**Registrar:** `{registrar}`\n"
        f"**Registration:** `{registration}`\n"
        f"**Expiration:** `{expiration}`\n"
        f"**Domain Available:** {domain_available}\n"
    )

    return details

async def ip_info_handler(client: Client, message: Message):
    if len(message.command) <= 1:
        await message.reply_text("**❌ Please provide a single IP address.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    ip = message.command[1]
    fetching_msg = await message.reply_text("**Fetching IP Info Please Wait.....**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    details = get_ip_info(ip)

    user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_profile_link = f"https://t.me/{message.from_user.username}"

    details += f"\n**Ip-Info Grab By:** [{user_full_name}]({user_profile_link})"

    await fetching_msg.delete()
    await message.reply_text(details, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

async def domain_info_handler(client: Client, message: Message):
    if len(message.command) <= 1:
        await message.reply_text("**❌ Please provide a valid domain name.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    fetching_msg = await message.reply_text("**Fetching Domain Information.....**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    domains = message.command[1:]
    details_list = []
    for domain in domains:
        details = get_domain_info(domain)
        details_list.append(details)
    
    details_combined = "\n".join(details_list)

    user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_profile_link = f"https://t.me/{message.from_user.username}"

    details_combined += f"\n**Domain Info Grab By:** [{user_full_name}]({user_profile_link})"

    await fetching_msg.delete()
    await message.reply_text(details_combined, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def setup_ip_handlers(app: Client):
    @app.on_message(filters.command("ip") & filters.private)
    async def ip_info(client: Client, message: Message):
        await ip_info_handler(client, message)

    @app.on_message(filters.command("dmn") & filters.private)
    async def domain_info(client: Client, message: Message):
        await domain_info_handler(client, message)

# To use the handler, call setup_ip_handlers(app) in your main script
