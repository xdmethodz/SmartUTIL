import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

# Helper function to generate cards
def generate_cards(bin_prefix, month, year, cvv, amount):
    cards = []
    for _ in range(amount):
        card_number = bin_prefix + ''.join(random.choices("0123456789", k=(16 - len(bin_prefix))))
        card_cvv = cvv if cvv != 'rnd' else ''.join(random.choices("0123456789", k=3))
        card_month = month if month != 'rnd' else f"{random.randint(1, 12):02}"
        card_year = year if year != 'rnd' else str(random.randint(2022, 2035))
        cards.append(f"{card_number}|{card_month}|{card_year}|{card_cvv}")
    return cards

def setup_card_gen_handlers(app: Client):
    @app.on_message(filters.command("gen") & filters.private)
    async def gen_handler(client: Client, message: Message):
        try:
            # Parse user input
            args = message.text.split()
            if len(args) < 2:
                await message.reply_text("Usage: `/gen <BIN> [Amount]`", parse_mode=ParseMode.MARKDOWN)
                return

            bin_prefix = args[1]
            amount = int(args[2]) if len(args) > 2 else 10

            # Validate inputs
            if len(bin_prefix) < 6 or not bin_prefix.isdigit():
                await message.reply_text("Invalid BIN format. BIN must be at least 6 digits.", parse_mode=ParseMode.MARKDOWN)
                return
            if amount <= 0 or amount > 100:
                await message.reply_text("Invalid amount. Must be between 1 and 100.", parse_mode=ParseMode.MARKDOWN)
                return

            # Generate cards
            cards = generate_cards(bin_prefix, 'rnd', 'rnd', 'rnd', amount)
            card_list = "\n".join(f"`{card}`" for card in cards)

            # Mock BIN information (replace with actual lookup logic if needed)
            bank = "N/A"
            country = "UNITED STATES"
            emoji = "🇺🇸"
            bin_info = "N/A - CREDIT - VISA"

            # Format response
            response = (
                f"**𝗕𝗜𝗡** ⇾ {bin_prefix}\n"
                f"**𝗔𝗺𝗼𝘂𝗻𝘁** ⇾ {amount}\n\n"
                f"{card_list}\n\n"
                f"**𝗕𝗮𝗻𝗸**: {bank}\n"
                f"**𝗖𝗼𝘂𝗻𝘁𝗿𝘆**: {country} {emoji}\n"
                f"**𝗕𝗜𝗡 𝗜𝗻𝗳𝗼**: {bin_info}"
            )

            # Inline button for regeneration
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔄 Regenerate", callback_data=f"regen|{bin_prefix}|{amount}")]]
            )

            # Send response
            await message.reply_text(response, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await message.reply_text(f"Error: {e}", parse_mode=ParseMode.MARKDOWN)

    @app.on_callback_query()
    async def callback_handler(client, callback_query):
        try:
            data = callback_query.data
            if data.startswith("regen"):
                _, bin_prefix, amount = data.split("|")
                amount = int(amount)

                # Generate cards
                cards = generate_cards(bin_prefix, 'rnd', 'rnd', 'rnd', amount)
                card_list = "\n".join(f"`{card}`" for card in cards)

                # Mock BIN information
                bank = "N/A"
                country = "UNITED STATES"
                emoji = "🇺🇸"
                bin_info = "N/A - CREDIT - VISA"

                # Format response
                response = (
                    f"**𝗕𝗜𝗡** ⇾ {bin_prefix}\n"
                    f"**𝗔𝗺𝗼𝘂𝗻𝘁** ⇾ {amount}\n\n"
                    f"{card_list}\n\n"
                    f"**𝗕𝗮𝗻𝗸**: {bank}\n"
                    f"**𝗖𝗼𝘂𝗻𝘁𝗿𝘆**: {country} {emoji}\n"
                    f"**𝗕𝗜𝗡 𝗜𝗻𝗳𝗼**: {bin_info}"
                )

                # Edit original message
                await callback_query.message.edit_text(response, reply_markup=callback_query.message.reply_markup, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await callback_query.message.reply_text(f"Error: {e}", parse_mode=ParseMode.MARKDOWN)

# To use the handler, call setup_card_gen_handlers(app) in your main script
