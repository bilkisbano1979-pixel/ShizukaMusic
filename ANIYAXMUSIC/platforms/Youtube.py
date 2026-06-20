import asyncio
import os
import re
import aiohttp
import json
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from ANIYAXMUSIC.utils.database import is_on_off
from ANIYAXMUSIC.utils.formatters import time_to_seconds

FALLBACK_API_URL = "https://shrutibots.site"
YOUR_API_URL = None

cookies_file = "ANIYAXMUSIC/assets/cookies.txt"


async def get_api_url():
    global YOUR_API_URL
    if YOUR_API_URL:
        return YOUR_API_URL
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://pastebin.com/raw/rLsBhAQa", timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    YOUR_API_URL = (await resp.text()).strip()
                else:
                    YOUR_API_URL = FALLBACK_API_URL
    except Exception:
        YOUR_API_URL = FALLBACK_API_URL
    return YOUR_API_URL


async def download_via_shruti(link: str, is_video: bool = False, retries: int = 3):
    api_url = await get_api_url()
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link

    folder = "downloads"
    if not os.path.exists(folder):
        os.makedirs(folder)

    ext = "mp4" if is_video else "mp3"
    file_path = os.path.join(folder, f"{video_id}.{ext}")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
        return file_path

    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                req_type = "video" if is_video else "audio"

                async with session.get(
                    f"{api_url}/download",
                    params={"url": video_id, "type": req_type},
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"Token request failed: {resp.status}")
                    data = await resp.json()
                    token = data.get("download_token")
                    if not token:
                        raise Exception("No download token received")

                stream_url = f"{api_url}/stream/{video_id}?type={req_type}"
                async with session.get(
                    stream_url,
                    headers={"X-Download-Token": token},
                    timeout=aiohttp.ClientTimeout(total=600),
                ) as resp:
                    if resp.status != 200:
                        raise Exception(f"Stream failed: {resp.status}")

                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(16384):
                            f.write(chunk)

                    if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
                        return file_path
                    raise Exception("Downloaded file is empty or too small")

        except Exception as e:
            print(f"⚠️ Shruti API attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                await asyncio.sleep(2 * attempt)
            else:
                print("❌ All Shruti API attempts failed, switching to yt-dlp fallback")

    return None


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


def _base_ytdlp_opts() -> dict:
    has_cookies = os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 10
    opts = {
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
        "extractor_args": {
            "youtube": {
                "player_client": ["android_music", "web"],
                "player_skip": [],
            }
        },
        "http_headers": {
            "User-Agent": "com.google.android.apps.youtube.music/7.11.50 (Linux; U; Android 13; en-US) gzip",
        },
    }
    if has_cookies:
        opts["cookiefile"] = cookies_file
    return opts


def _ytdlp_extract_info(link: str) -> dict:
    opts = _base_ytdlp_opts()
    opts["skip_download"] = True
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(link, download=False)


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset: offset + length]

    async def _search_ytdlp(self, query: str):
        """Search YouTube using extract_flat=True so we never hit individual video
        endpoints — avoids the 'Sign in to confirm you're not a bot' block."""
        loop = asyncio.get_running_loop()
        def _do():
            opts = {
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": "in_playlist",  # Only metadata, no per-video requests
                "noplaylist": False,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                entries = info.get("entries", [])
                if not entries:
                    raise Exception("No results found")
                e = entries[0]
                vid_id = e.get("id", "")
                dur = e.get("duration", 0) or 0
                return {
                    "id": vid_id,
                    "title": e.get("title", "Unknown"),
                    "duration": dur,
                    "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg",
                    "webpage_url": e.get("url") or f"https://www.youtube.com/watch?v={vid_id}",
                }
        return await loop.run_in_executor(None, _do)

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        try:
            result = await self._search_ytdlp(link)
            title = result.get("title", "Unknown")
            duration_sec_raw = result.get("duration", 0) or 0
            mins = int(duration_sec_raw) // 60
            secs = int(duration_sec_raw) % 60
            duration_min = f"{mins}:{secs:02d}"
            thumbnail = result.get("thumbnail", "")
            vidid = result.get("id", "")
        except Exception as e:
            raise Exception(f"details() failed: {e}")

        if str(duration_min) == "None":
            duration_sec = 0
        else:
            duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        r = await self._search_ytdlp(link)
        return r.get("title", "Unknown")

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        r = await self._search_ytdlp(link)
        dur = r.get("duration", 0) or 0
        mins = int(dur) // 60
        secs = int(dur) % 60
        return f"{mins}:{secs:02d}"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        r = await self._search_ytdlp(link)
        return r.get("thumbnail", "")

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        has_cookies = os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 10
        cookie_arg = f"--cookies {cookies_file}" if has_cookies else ""
        playlist = await shell_cmd(
            f"yt-dlp {cookie_arg} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            result = [key for key in result if key]
        except Exception:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        result = await self._search_ytdlp(link)
        title = result.get("title", "Unknown")
        vidid = result.get("id", "")
        yturl = result.get("webpage_url", self.base + vidid)
        dur = result.get("duration", 0) or 0
        mins = int(dur) // 60
        secs = int(dur) % 60
        duration_min = f"{mins}:{secs:02d}"
        thumbnail = result.get("thumbnail", "")

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = _base_ytdlp_opts()
        ytdl_opts["skip_download"] = True
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(
        self, link: str, query_type: int, videoid: Union[bool, str] = None
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        r = await self._search_ytdlp(link)
        vidid = r.get("id", "")
        dur = r.get("duration", 0) or 0
        mins = int(dur) // 60
        secs = int(dur) % 60
        duration_min = f"{mins}:{secs:02d}"
        return r.get("title", "Unknown"), duration_min, r.get("thumbnail", ""), vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        is_video_req = True if (video or songvideo) else False

        try:
            downloaded_file = await download_via_shruti(link, is_video=is_video_req, retries=3)
            if downloaded_file:
                return downloaded_file, True
        except Exception as e:
            print(f"⚠️ Shruti API completely failed: {e}")

        loop = asyncio.get_running_loop()

        def build_ydl_opts(is_vid: bool) -> dict:
            opts = _base_ytdlp_opts()
            opts["outtmpl"] = "downloads/%(id)s.%(ext)s"
            opts["no_part"] = True
            if is_vid:
                opts["format"] = (
                    "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])/best[height<=?720]"
                )
                opts["merge_output_format"] = "mp4"
            else:
                opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            return opts

        def ytdlp_dl(is_vid: bool):
            opts = build_ydl_opts(is_vid)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                vid_id = info["id"]
                ext = "mp4" if is_vid else "mp3"
                file_path = os.path.join("downloads", f"{vid_id}.{ext}")
                if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
                    return file_path
                ydl.download([link])
                if os.path.exists(file_path):
                    return file_path
                webm_path = os.path.join("downloads", f"{vid_id}.webm")
                if os.path.exists(webm_path):
                    return webm_path
                m4a_path = os.path.join("downloads", f"{vid_id}.m4a")
                if os.path.exists(m4a_path):
                    return m4a_path
                return file_path

        for attempt in range(1, 4):
            try:
                downloaded_file = await loop.run_in_executor(
                    None, ytdlp_dl, is_video_req
                )
                if downloaded_file and os.path.exists(downloaded_file):
                    return downloaded_file, True
            except Exception as e:
                print(f"⚠️ yt-dlp attempt {attempt}/3 failed: {e}")
                if attempt < 3:
                    await asyncio.sleep(3 * attempt)

        raise Exception("All download methods failed after retries.")

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        if stdout:
            url = stdout.decode().strip().split("\n")[0]
            return 1, url
        return 0, None
