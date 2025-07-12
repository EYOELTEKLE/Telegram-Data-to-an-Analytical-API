import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from src.utils.safe_dumper import safe_serialize  # Must handle datetime deeply

# Load environment variables
load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION = os.getenv('TELEGRAM_SESSION', 'anon')

CHANNELS = [
    'https://t.me/lobelia4cosmetics',
    'https://t.me/tikvahpharma',
    # Add more from https://et.tgstat.com/medicine
]

# Base data lake paths
RAW_MSG_DIR = Path('data/raw/telegram_messages')
RAW_IMG_DIR = Path('data/raw/telegram_images')

# Setup logging
logging.basicConfig(
    filename='scrape_telegram.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def get_channel_name(url: str):
    return url.rstrip('/').split('/')[-1]

async def scrape_channel(client, channel_url, msg_out_file, img_out_dir):
    messages = []
    channel_name = get_channel_name(channel_url)

    try:
        logger.info(f"Scraping: {channel_name}")
        async for message in client.iter_messages(channel_url, limit=1000):
            msg_dict = message.to_dict()
            messages.append(msg_dict)

            # --- Handle image or media download ---
            if message.media:
                try:
                    ensure_dir(img_out_dir)
                    file_path = img_out_dir / f"{message.id}"
                    await client.download_media(message, file=file_path)
                    logger.info(f"Downloaded media from message {message.id} in {channel_name}")
                except Exception as media_err:
                    logger.warning(f"Media download failed for {channel_name} message {message.id}: {media_err}")

        # Save messages as JSON
        with open(msg_out_file, 'w', encoding='utf-8') as f:
            json.dump(safe_serialize(messages), f, ensure_ascii=False, indent=2)

        logger.info(f"✅ Finished scraping {len(messages)} messages from {channel_name}")

    except FloodWaitError as e:
        logger.warning(f"⚠️ Flood wait for {channel_name}: sleeping for {e.seconds} sec")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"❌ Error scraping {channel_name}: {e}")

async def main():
    if not API_ID or not API_HASH:
        logger.error("Missing TELEGRAM_API_ID or TELEGRAM_API_HASH in .env")
        return

    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    today_str = datetime.now().strftime('%Y-%m-%d')

    for channel_url in CHANNELS:
        channel_name = get_channel_name(channel_url)

        # Directories
        msg_dir = RAW_MSG_DIR / today_str
        img_dir = RAW_IMG_DIR / today_str / channel_name
        ensure_dir(msg_dir)

        msg_out_file = msg_dir / f"{channel_name}.json"
        await scrape_channel(client, channel_url, msg_out_file, img_dir)

        await asyncio.sleep(3)  # Delay between channels

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
