from faker import Faker
from pyrogram import filters
from pyrogram.enums import ParseMode
import asyncio

faker = Faker()

def setup_fake_handler(app):
    @app.on_message(filters.command("fake") & filters.private)
    async def generate_fake_address(client, message):
        # Check if the user provided a country code
        if len(message.command) == 1:
            await message.reply_text(
                "<b>❌ Provide a valid country name or country code.</b>",
                parse_mode=ParseMode.HTML
            )
            return

        country_code = message.text.split()[1]

        try:
            # Set Faker locale to the provided country code
            fake = Faker(locale=country_code)
        except Exception:
            await message.reply_text(
                "<b>❌ Invalid country code. Please try again.</b>",
                parse_mode=ParseMode.HTML
            )
            return

        # Send animation message
        anim_msg = await message.reply_text(
            f"<b>Generating Fake Address for {country_code}...</b>",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        await anim_msg.delete()

        # Generate fake address details
        full_name = fake.name()
        gender = fake.random_element(["Male", "Female"])
        street = fake.street_address()
        city = fake.city()
        state = fake.state()
        postal_code = fake.postcode()
        phone_number = fake.phone_number()
        country = fake.current_country()

        # Send fake address
        await message.reply_text(
            f"<b>Address for {country}:</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"Full Name: <code>{full_name}</code>\n"
            f"Gender: <code>{gender}</code>\n"
            f"Street: <code>{street}</code>\n"
            f"City/Town/Village: <code>{city}</code>\n"
            f"State/Province/Region: <code>{state}</code>\n"
            f"Postal code: <code>{postal_code}</code>\n"
            f"Phone Number: <code>{phone_number}</code>\n"
            f"Country: <code>{country}</code>",
            parse_mode=ParseMode.HTML
        )
