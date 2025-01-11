import os
import logging
from pathlib import Path
from typing import Optional
import aiohttp
import re
import json
import yt_dlp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    TEMP_DIR = Path("temp")
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.pinterest.com/',
    }

Config.TEMP_DIR.mkdir(exist_ok=True)

class FacebookDownloader:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        yt_dlp.utils.std_headers['User-Agent'] = Config.HEADERS['User-Agent']

    def download_video(self, url: str) -> Optional[str]:
        self.temp_dir.mkdir(exist_ok=True)
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(str(self.temp_dir), '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'simulate': False,
            'nooverwrites': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)
                if os.path.exists(filename):
                    return filename
                else:
                    return None
        except Exception as e:
            logger.error(f"Facebook download error: {e}")
            return None

class PinterestDownloader:
    def __init__(self):
        self.session = None
        self.pin_patterns = [
            r'/pin/(\d+)',
            r'pin/(\d+)',
            r'pin_id=(\d+)'
        ]
        
    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=Config.HEADERS)

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def extract_pin_id(self, url: str) -> Optional[str]:
        await self.init_session()
        
        if 'pin.it' in url:
            async with self.session.head(url, allow_redirects=True) as response:
                url = str(response.url)
        
        for pattern in self.pin_patterns:
            if match := re.search(pattern, url):
                return match.group(1)
        return None

    def get_highest_quality_image(self, image_url: str) -> str:
        url = re.sub(r'/\d+x/|/\d+x\d+/', '/originals/', image_url)
        url = re.sub(r'\?.+$', '', url)
        return url

    async def get_pin_data(self, pin_id: str) -> Optional[str]:
        url = f"https://www.pinterest.com/pin/{pin_id}/"
        
        async with self.session.get(url) as response:
            if response.status == 200:
                text = await response.text()
                video_matches = re.findall(r'"url":"([^"]*?\.mp4[^"]*)"', text)
                if video_matches:
                    return unquote(video_matches[0].replace('\\/', '/'))
                image_patterns = [
                    r'<meta property="og:image" content="([^"]+)"',
                    r'"originImageUrl":"([^"]+)"',
                    r'"image_url":"([^"]+)"',
                ]
                
                for pattern in image_patterns:
                    if matches := re.findall(pattern, text):
                        for match in matches:
                            image_url = unquote(match.replace('\\/', '/'))
                            if any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                return self.get_highest_quality_image(image_url)
        return None

def setup_dl_handlers(app: Client):
    fb_downloader = FacebookDownloader(Config.TEMP_DIR)
    pin_downloader = PinterestDownloader()

    @app.on_message(filters.command("fb") & filters.private)
    async def fb_handler(client: Client, message: Message):
        if len(message.command) <= 1:
            await message.reply_text("**Please provide a Facebook video URL after the command.**", parse_mode=ParseMode.MARKDOWN)
            return
        
        url = message.command[1]
        downloading_message = await message.reply_text("`Searching The Video`", parse_mode=ParseMode.MARKDOWN)
        
        try:
            filename = await asyncio.to_thread(fb_downloader.download_video, url)
            if filename:
                await downloading_message.edit_text("`Downloading Your Video ...`", parse_mode=ParseMode.MARKDOWN)
                max_telegram_size = 50 * 1024 * 1024
                
                with open(filename, 'rb') as video_file:
                    file_size = os.path.getsize(filename)
                    if file_size > max_telegram_size:
                        await message.reply_document(document=video_file, caption="Large Video")
                    else:
                        await message.reply_video(video=video_file, supports_streaming=True)
                
                await downloading_message.delete()
                os.remove(filename)
            else:
                await downloading_message.edit_text("Could not download the video.")
        except Exception as e:
            logger.error(f"Error downloading Facebook video: {e}")
            await downloading_message.edit_text("An error occurred while processing your request.")

    @app.on_message(filters.command("pin") & filters.private)
    async def pin_handler(client: Client, message: Message):
        if len(message.command) <= 1:
            await message.reply_text("**Please provide a valid Pinterest video URL.**", parse_mode=ParseMode.MARKDOWN)
            return
        
        url = message.command[1]
        downloading_message = await message.reply_text("`Searching The Video`", parse_mode=ParseMode.MARKDOWN)
        
        try:
            pin_id = await pin_downloader.extract_pin_id(url)
            if not pin_id:
                await downloading_message.edit_text("Invalid Pinterest URL.")
                return
            
            media_url = await pin_downloader.get_pin_data(pin_id)
            if not media_url:
                await downloading_message.edit_text("Could not find media in this Pinterest link.")
                return
            
            await downloading_message.edit_text("`Downloading Your Video ...`", parse_mode=ParseMode.MARKDOWN)
            file_path = Config.TEMP_DIR / f"temp_{message.chat.id}_{pin_id}"
            file_path = file_path.with_suffix('.mp4' if media_url.endswith('.mp4') else '.jpg')
            
            async with pin_downloader.session.get(media_url) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        while chunk := await response.content.read(8192):
                            f.write(chunk)
            
            with open(file_path, 'rb') as media_file:
                if file_path.suffix == '.mp4':
                    await message.reply_video(video=media_file, supports_streaming=True)
                else:
                    await message.reply_photo(photo=media_file)
            
            await downloading_message.delete()
            os.remove(file_path)
        except Exception as e:
            logger.error(f"Error downloading Pinterest media: {e}")
            await downloading_message.edit_text("An error occurred while processing your request.")

# To use the handler, call setup_dl_handlers(app) in your main script
