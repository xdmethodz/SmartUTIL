import requests
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

def get_crypto_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Invalid token symbol or data unavailable for {symbol}")
    data = response.json()
    return data

def setup_binance_handler(app: Client):
    @app.on_message(filters.command("price") & filters.private)
    async def handle_price_command(client, message):
        if len(message.command) == 1 and not message.reply_to_message:
            await message.reply_text(
                "<b>Specify a valid cryptocurrency name. e.g. /price BTC</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            token = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else message.reply_to_message.text
            fetching_message = await message.reply_text(
                "<b>Fetching token data, please wait...</b>",
                parse_mode=ParseMode.HTML
            )
            try:
                data = get_crypto_data(token)
                result = (
                    f"<b>{token} (USDT)</b>\n"
                    f"    🔸 <b>Price:</b> <code>${data['lastPrice']} USDT</code>\n"
                    f"    🔸 <b>24hr Change:</b> <code>{data['priceChangePercent']}%</code>\n"
                    f"    🔸 <b>24hr High:</b> <code>${data['highPrice']} USDT</code>\n"
                    f"    🔸 <b>24hr Low:</b> <code>${data['lowPrice']} USDT</code>\n"
                )
                await fetching_message.delete()
                await message.reply_text(result, parse_mode=ParseMode.HTML)
            except ValueError as e:
                await fetching_message.delete()
                await message.reply_text(
                    f"<b>{str(e)}</b>",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                await fetching_message.delete()
                await message.reply_text(
                    f"<b>An unexpected error occurred:</b> {str(e)}",
                    parse_mode=ParseMode.HTML
                )

# To use the handler, call setup_binance_handler(app) in your main script