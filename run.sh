#!/bin/bash
set -e

echo "=== Izumi Music Bot Starting ==="

echo "[1/3] Installing Python packages..."
pip install --quiet \
  aiofiles aiohttp apscheduler beautifulsoup4 bs4 cloudscraper \
  dnspython emojis ffmpeg-python Faker future gitpython gpytranslate gtts \
  hachoir httpx img2pdf instaloader motor numpy Pillow psutil pickledb \
  pycountry pycryptodome pydub pyfiglet python-dotenv python-whois \
  pyshorteners pytz pytube pyyaml qrcode requests speedtest-cli spotipy \
  telegraph tgcrypto unidecode wget youtube-search youtube-search-python \
  SpeechRecognition pymongo

echo "[2/3] Installing pytgcalls 0.9.7..."
pip install --quiet "py-tgcalls==0.9.7"

echo "[2.5/3] Installing git packages..."
pip install --quiet "git+https://github.com/KurimuzonAkuma/pyrogram"
pip install --quiet "git+https://github.com/yt-dlp/yt-dlp"
pip install --quiet "git+https://github.com/AsmSafone/SafoneAPI" || true

echo "[3/3] Starting bot..."
# Export BOT_TOKEN from Replit secret (overrides any .env file value)
export BOT_TOKEN="${BOT_TOKEN}"
export API_ID="${API_ID}"
export API_HASH="${API_HASH}"
python3 -m ANIYAXMUSIC
