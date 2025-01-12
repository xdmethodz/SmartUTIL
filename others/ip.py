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
    url = f"https://api.domainsdb.info/v1/domains/search?domain={domain}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Invalid domain name: {domain}"

    data = response.json()
    if "domains" not in data or not data["domains"]:
        return f"Invalid domain name: {domain}"

    domain_info = data["domains"][0]
    domain_name = domain_info.get("domain", "Unknown")
    registrar = domain_info.get("registrar", "Unknown")
    registration = domain_info.get("create_date", "Unknown")
    expiration = domain_info.get("update_date", "Unknown")
    domain_available = "✅" if domain_info.get("isDead", False) else "❌"

    details = (
        f"**Domain:** `{domain_name}`\n"
        f"**Registrar:** `{registrar}`\n"
        f"**Registration:** `{registration}`\n"
        f"**Expiration:** `{expiration}`\n"
        f"**Domain Available:** {domain_available}\n"
    )

    return details

def check_proxy(proxy: str, auth: tuple = None) -> str:
    url = "http://ipinfo.io/json"
    proxies = {
        "http": f"http://{proxy}",
        "https": f"https://{proxy}",
    }
    try:
        response = requests.get(url, proxies=proxies, auth=auth, timeout=10)
        if response.status_code == 200:
            data = response.json()
            region = data.get("region", "Unknown")
            return (
                f"**Proxy:** `{proxy}`\n"
                f"**Type:** `HTTP/HTTPS`\n"
                f"**Status:** ☑️ `Alive`\n"
                f"**Region:** `{region}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
            )
        else:
            return (
                f"**Proxy:** `{proxy}`\n"
                f"**Type:** `HTTP/HTTPS`\n"
                f"**Status:** 🔴 `Dead`\n"
                f"**Region:** `Unknown`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
            )
    except requests.RequestException as e:
        return (
            f"**Proxy:** `{proxy}`\n"
            f"**Type:** `HTTP/HTTPS`\n"
            f"**Status:** 🔴 `Dead`\n"
            f"**Region:** `Unknown`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
        )

async def ip_info_handler(client: Client, message: Message):
    if len(message.command) <= 1:
        await message.reply_text("**❌ Please provide a single IP address.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    ip = message.command[1]
    fetching_msg = await message.reply_text("**Fetching IP Info Please Wait.....**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    details = get_ip_info(ip)

    user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_profile_link = f"https://t.me/{message.from_user.username}"

    details += f"**Ip-Info Grab By:** [{user_full_name}]({user_profile_link})"

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

async def proxy_info_handler(client: Client, message: Message):
    if len(message.command) <= 1:
        await message.reply_text("**❌ Please provide at least one proxy.**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return

    proxies = message.command[1:]
    auth = None

    if len(proxies) >= 3 and ':' not in proxies[-1]:
        user = proxies[-2]
        password = proxies[-1]
        auth = (user, password)
        proxies = proxies[:-2]

    fetching_msg = await message.reply_text("**Checking Proxies Please Wait.....**", parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    details_list = []
    for proxy in proxies:
        details = check_proxy(proxy, auth)
        details_list.append(details)
    
    details_combined = "\n".join(details_list)

    user_full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_profile_link = f"https://t.me/{message.from_user.username}"

    details_combined += f"\n**Proxies Checked By:** [{user_full_name}]({user_profile_link})"

    await fetching_msg.delete()
    await message.reply_text(details_combined, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

def setup_ip_handlers(app: Client):
    @app.on_message(filters.command("ip") & filters.private)
    async def ip_info(client: Client, message: Message):
        await ip_info_handler(client, message)

    @app.on_message(filters.command("dmn") & filters.private)
    async def domain_info(client: Client, message: Message):
        await domain_info_handler(client, message)

    @app.on_message(filters.command("px") & filters.private)
    async def proxy_info(client: Client, message: Message):
        await proxy_info_handler(client, message)

# To use the handler, call setup_ip_handlers(app) in your main script
