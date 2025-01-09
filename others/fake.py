import pycountry
from pyrogram import Client, filters
from pyrogram.types import Message
from faker import Faker
from pyrogram.enums import ParseMode
from asyncio import sleep

# List of countries with fundamental information
countries_info = [
    {
        "name": "Bangladesh", 
        "alpha_2": "BD", 
        "phone_format": "+880XXXXXXXXXX",
        "cities": ["Dhaka", "Chittagong", "Khulna"],
        "regions": ["Dhaka Division", "Chittagong Division", "Khulna Division"],
        "postal_codes": ["1000", "4000", "9000"],
        "streets": ["Main Road", "Station Road", "Lake Road"]
    },
    {
        "name": "India", 
        "alpha_2": "IN", 
        "phone_format": "+91XXXXXXXXXX",
        "cities": ["Mumbai", "Delhi", "Bangalore"],
        "regions": ["Maharashtra", "Delhi", "Karnataka"],
        "postal_codes": ["400001", "110001", "560001"],
        "streets": ["MG Road", "Ring Road", "Brigade Road"]
    },
    {
        "name": "Pakistan", 
        "alpha_2": "PK", 
        "phone_format": "+92XXXXXXXXXX",
        "cities": ["Karachi", "Lahore", "Islamabad"],
        "regions": ["Sindh", "Punjab", "Islamabad Capital Territory"],
        "postal_codes": ["74000", "54000", "44000"],
        "streets": ["Shahrah-e-Faisal", "Mall Road", "Constitution Avenue"]
    },
    {
        "name": "Algeria", 
        "alpha_2": "DZ", 
        "phone_format": "+213XXXXXXXXX",
        "cities": ["Algiers", "Oran", "Constantine"],
        "regions": ["Algiers Province", "Oran Province", "Constantine Province"],
        "postal_codes": ["16000", "31000", "25000"],
        "streets": ["Rue Didouche Mourad", "Rue Larbi Ben M'hidi", "Rue Hassiba Ben Bouali"]
    },
    {
        "name": "United States", 
        "alpha_2": "US", 
        "phone_format": "+1XXXXXXXXXX",
        "cities": ["New York", "Los Angeles", "Chicago"],
        "regions": ["New York", "California", "Illinois"],
        "postal_codes": ["10001", "90001", "60601"],
        "streets": ["5th Avenue", "Sunset Boulevard", "Michigan Avenue"]
    },
    {
        "name": "United Kingdom", 
        "alpha_2": "GB", 
        "phone_format": "+44XXXXXXXXXX",
        "cities": ["London", "Manchester", "Birmingham"],
        "regions": ["England", "Greater Manchester", "West Midlands"],
        "postal_codes": ["EC1A", "M1", "B1"],
        "streets": ["Baker Street", "Oxford Road", "High Street"]
    },
    # Add more countries with their details similarly...
]

def get_country_info(alpha_2):
    for country in countries_info:
        if country["alpha_2"] == alpha_2:
            return country
    return None

def setup_fake_handler(app: Client):
    @app.on_message(filters.command("fake"))
    async def fake_handler(client: Client, message: Message):
        if len(message.command) <= 1:
            await message.reply_text("**❌ Provide a valid country name or country code.**")
            return
        
        country_code = message.command[1]
        country = pycountry.countries.get(alpha_2=country_code.upper()) or pycountry.countries.get(name=country_code.title())
        
        if not country:
            await message.reply_text("**❌ Provide a valid country name or country code.**")
            return

        # Get country info from the predefined list
        country_info = get_country_info(country.alpha_2)
        
        if not country_info:
            await message.reply_text("**❌ Country details not available.**")
            return

        fake = Faker()

        # Generate fake details
        full_name = fake.name() or "N/A"
        gender = fake.random_element(elements=("Male", "Female")) or "N/A"
        street = fake.random_element(elements=country_info["streets"]) or "N/A"
        city = fake.random_element(elements=country_info["cities"]) or "N/A"
        state = fake.random_element(elements=country_info["regions"]) or "N/A"
        postal_code = fake.random_element(elements=country_info["postal_codes"]) or "N/A"
        phone_number = generate_phone_number(fake, country_info["phone_format"]) or "N/A"
        country_name = country.name
        
        generating_message = await message.reply_text(f"**Generating Fake Address For {country_name}...**")
        await sleep(2)
        await generating_message.delete()
        
        await message.reply_text(f"""
**Address for {country_name}:**
━━━━━━━━━━━━━━━━━
**Full Name:** `{full_name}`
**Gender:** `{gender}`
**Street:** `{street}`
**City/Town/Village:** `{city}`
**State/Province/Region:** `{state}`
**Postal code:** `{postal_code}`
**Phone Number:** `{phone_number}`
**Country:** `{country_name}`
""", parse_mode=ParseMode.MARKDOWN)

def generate_phone_number(fake, phone_format):
    """
    Generate a phone number based on the country phone format.
    """
    phone_number = phone_format
    for _ in range(phone_number.count('X')):
        phone_number = phone_number.replace('X', str(fake.random_digit()), 1)
    return phone_number
