from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

# Helper function to generate cards
def generate_cards(bin_prefix, month, year, amount):
    cards = []
    for _ in range(amount):
        card_number = bin_prefix + ''.join(random.choices("0123456789", k=(16 - len(bin_prefix))))
        cvv = ''.join(random.choices("0123456789", k=3))
        cards.append(f"{card_number}|{month}|{year}|{cvv}")
    return cards

def setup_card_gen_handlers(app: Client):
    # Command handler for /gen
    @app.on_message(filters.command("gen") & filters.private)
    async def gen_handler(client, message):
        try:
            # Parse user input
            args = message.text.split()
            if len(args) < 4:
                await message.reply_text("Usage: `/gen <BIN> <MM|YY> <AMOUNT>`", parse_mode="markdown")
                return

            bin_prefix = args[1]
            month, year = args[2].split("|")
            amount = int(args[3])

            # Validate inputs
            if len(bin_prefix) < 6 or not bin_prefix.isdigit():
                await message.reply_text("Invalid BIN format. BIN must be at least 6 digits.")
                return
            if not month.isdigit() or not year.isdigit() or int(month) < 1 or int(month) > 12:
                await message.reply_text("Invalid month/year format. Use MM|YY (e.g., 05|26).")
                return
            if amount <= 0 or amount > 50:
                await message.reply_text("Invalid amount. Must be between 1 and 50.")
                return

            # Generate cards
            cards = generate_cards(bin_prefix, month, year, amount)
            card_list = "\n".join(f"`{card}`" for card in cards)

            # Mock BIN information (replace with actual lookup logic if needed)
            bank = "N/A"
            country = "UNITED STATES"
            emoji = "🇺🇸"
            bin_info = "N/A - CREDIT - VISA"

            # Format response
            response = (
                f"𝗕𝗜𝗡 ⇾ {bin_prefix}\n"
                f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {amount}\n\n"
                f"{card_list}\n\n"
                f"𝗕𝗮𝗻𝗸: {bank}\n"
                f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {emoji}\n"
                f"𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {bin_info}"
            )

            # Inline button for regeneration
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔄 Regenerate", callback_data=f"regen|{bin_prefix}|{month}|{year}|{amount}")]]
            )

            # Send response
            await message.reply_text(response, reply_markup=buttons, parse_mode="markdown")
        except Exception as e:
            await message.reply_text(f"Error: {e}")

    # Callback handler for regeneration
    @app.on_callback_query()
    async def callback_handler(client, callback_query):
        try:
            data = callback_query.data
            if data.startswith("regen"):
                _, bin_prefix, month, year, amount = data.split("|")
                amount = int(amount)

                # Generate cards
                cards = generate_cards(bin_prefix, month, year, amount)
                card_list = "\n".join(f"`{card}`" for card in cards)

                # Mock BIN information
                bank = "N/A"
                country = "UNITED STATES"
                emoji = "🇺🇸"
                bin_info = "N/A - CREDIT - VISA"

                # Format response
                response = (
                    f"𝗕𝗜𝗡 ⇾ {bin_prefix}\n"
                    f"𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ {amount}\n\n"
                    f"{card_list}\n\n"
                    f"𝗕𝗮𝗻𝗸: {bank}\n"
                    f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {emoji}\n"
                    f"𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {bin_info}"
                )

                # Edit original message
                await callback_query.message.edit_text(response, reply_markup=callback_query.message.reply_markup, parse_mode="markdown")
        except Exception as e:
            await callback_query.message.reply_text(f"Error: {e}")