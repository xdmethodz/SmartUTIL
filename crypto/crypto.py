import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BASE_URL = "https://api.binance.com/api/v3/ticker/24hr"

def fetch_crypto_data():
    response = requests.get(BASE_URL)
    response.raise_for_status()
    return response.json()

def get_top_gainers(data, top_n=5):
    sorted_data = sorted(data, key=lambda x: float(x['priceChangePercent']), reverse=True)
    return sorted_data[:top_n]

def get_top_losers(data, top_n=5):
    sorted_data = sorted(data, key=lambda x: float(x['priceChangePercent']))
    return sorted_data[:top_n]

def format_crypto_info(data, start_index=0):
    result = ""
    for idx, item in enumerate(data, start=start_index + 1):
        result += (
            f"<b>{idx}. Symbol:</b> {item['symbol']}\n"
            f"  <b>Change:</b> {item['priceChangePercent']}%\n"
            f"  <b>Last Price:</b> {item['lastPrice']}\n"
            f"  <b>24h High:</b> {item['highPrice']}\n"
            f"  <b>24h Low:</b> {item['lowPrice']}\n"
            f"  <b>24h Volume:</b> {item['volume']}\n"
            f"  <b>24h Quote Volume:</b> {item['quoteVolume']}\n\n"
        )
    return result

def setup_crypto_handler(app: Client):
    @app.on_message(filters.command(["gainers", "losers"]) & filters.private)
    async def handle_command(client, message):
        command = message.command[0]
        fetching_message = await message.reply(f"<b>Fetching {command}...</b>", parse_mode=ParseMode.HTML)
        
        try:
            data = fetch_crypto_data()
            top_n = 5
            if command == "gainers":
                top_cryptos = get_top_gainers(data, top_n)
                title = "Gainers"
            else:
                top_cryptos = get_top_losers(data, top_n)
                title = "Losers"

            formatted_info = format_crypto_info(top_cryptos)
            await fetching_message.delete()
            response_message = f"<b>📈List Of Top {title}:</b>\n\n{formatted_info}"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Next", callback_data=f"{command}_1")]
            ])
            await message.reply(response_message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

        except Exception as e:
            await fetching_message.delete()
            await message.reply(f"<b>Error fetching data: {str(e)}</b>", parse_mode=ParseMode.HTML)

    @app.on_callback_query(filters.regex(r"^(gainers|losers)_\d+"))
    async def handle_pagination(client, callback_query):
        command, page = callback_query.data.split('_')
        page = int(page)
        next_page = page + 1
        prev_page = page - 1

        try:
            data = fetch_crypto_data()
            top_n = 5
            if command == "gainers":
                top_cryptos = get_top_gainers(data, top_n * next_page)[(page-1)*top_n:page*top_n]
                title = "Gainers"
            else:
                top_cryptos = get_top_losers(data, top_n * next_page)[(page-1)*top_n:page*top_n]
                title = "Losers"

            formatted_info = format_crypto_info(top_cryptos, start_index=(page-1)*top_n)
            response_message = f"<b>📈List Of Top {title}:</b>\n\n{formatted_info}"

            keyboard_buttons = []
            if prev_page > 0:
                keyboard_buttons.append(InlineKeyboardButton("Previous", callback_data=f"{command}_{prev_page}"))
            if len(top_cryptos) == top_n:
                keyboard_buttons.append(InlineKeyboardButton("Next", callback_data=f"{command}_{next_page}"))

            keyboard = InlineKeyboardMarkup([keyboard_buttons])
            await callback_query.message.edit_text(response_message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

        except Exception as e:
            await callback_query.message.edit_text(f"<b>Error fetching data: {str(e)}</b>", parse_mode=ParseMode.HTML)

# To use the handler, call setup_crypto_handler(app) in your main script