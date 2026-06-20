import time
import random
import asyncio
import traceback
import aiohttp 
import json
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import CallbackQuery
from youtubesearchpython.__future__ import VideosSearch

import config
from ANIYAXMUSIC import app
from ANIYAXMUSIC.misc import _boot_
from ANIYAXMUSIC.plugins.sudo.sudoers import sudoers_list
from ANIYAXMUSIC.utils.database import get_served_chats, get_served_users, get_sudoers
from ANIYAXMUSIC.utils import bot_sys_stats
from ANIYAXMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from ANIYAXMUSIC.utils.decorators.language import LanguageStart
from ANIYAXMUSIC.utils.formatters import get_readable_time
from ANIYAXMUSIC.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

import os as _os
_ASSET_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "assets")

YUMI_PICS = [
    _os.path.join(_ASSET_DIR, "shizuka.jpg"),
]

START_VIDEO_PATH = None

# Sticker from Aestheticaddahee_by_fStikBot pack (sticker #67, 0-indexed: 66)
VENATRIX_STICKER_ID = None

# <emoji id='6181573775742472851'>🔥</emoji> PROMO MEIN CUSTOM EMOJIS
PROMO =  "───────────────────────\n<emoji id='6179286082887095182'>💀</emoji> <b>ᴘᴧɪᴅ ᴘʀσϻσᴛɪση ᴧᴠᴧɪʟᴧʙʟє</b> <emoji id='6179286082887095182'>💀</emoji>\n───────────────────────\n<blockquote><emoji id='6179444721799139547'>😉</emoji> ᴄʜᴧᴛᴛɪηɢ ɢʀσυᴘ's\n<emoji id='5219901967916084166'>😈</emoji> ᴄσʟσʀ ᴛʀᴧᴅɪηɢ ɢᴧϻє's\n<emoji id='6233067568878326937'>🐾</emoji> ᴄʜᴧηηєʟ's | ɢʀσυᴘ's .....\n<emoji id='5219943216781995020'>🔫</emoji> ʙєᴛᴛɪηɢ ᴧᴅs σʀ ᴧηʏᴛʜɪηɢ</blockquote>\n\n───────────────────────\n<emoji id='6179312501230932111'>😎</emoji> <b>ᴘʟᴧηꜱ -</b>\n<blockquote>||<emoji id='5357592447557848986'>☠️</emoji> ᴅᴧɪʟʏ\n<emoji id='5357592447557848986'>☠️</emoji> ᴡєєᴋʟʏ\n<emoji id='5357592447557848986'>☠️</emoji> ϻσηᴛʜʟʏ||</blockquote>\n───────────────────────\n<emoji id='6179275401303430193'>💖</emoji> <b>ᴄσηᴛᴧᴄᴛ -</b> <a href='https://t.me/hehe_stalker'>愛 | 𝗦𝗧么𝗟𝗞𝚵𝗥</a>\n───────────────────────"

GREET = ["<emoji id='6179042566831348153'>💞</emoji>", "🥂", "🔍", "🧪", "🥂", "⚡️", "<emoji id='6181573775742472851'>🔥</emoji>"]

# <emoji id='6181573775742472851'>🔥</emoji> INJECT PREMIUM BUTTONS
async def inject_premium_markup(chat_id, message_id, markup):
    try:
        token = getattr(config, "BOT_TOKEN", getattr(app, "bot_token", None))
        url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
        payload = {"chat_id": chat_id, "message_id": message_id, "reply_markup": {"inline_keyboard": markup}}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        print(f"❌ CODE CRASH: {e}")

# <emoji id='6181573775742472851'>🔥</emoji> FETCH STICKER FROM PACK ON STARTUP (Bot API se direct)
async def fetch_venatrix_sticker():
    global VENATRIX_STICKER_ID
    try:
        token = getattr(config, "BOT_TOKEN", None)
        if not token:
            return
        url = f"https://api.telegram.org/bot{token}/getStickerSet?name=Aestheticaddahee_by_fStikBot"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res = await resp.json()
                if res.get("ok"):
                    stickers = res["result"]["stickers"]
                    if len(stickers) >= 28:
                        VENATRIX_STICKER_ID = stickers[27]["file_id"]
                    elif stickers:
                        VENATRIX_STICKER_ID = stickers[-1]["file_id"]
                    print(f"<emoji id='6179474365663417710'>✅</emoji> Sticker fetched: {VENATRIX_STICKER_ID[:20]}...")
                else:
                    print(f"⚠️ getStickerSet failed: {res}")
    except Exception as e:
        print(f"⚠️ Could not fetch sticker pack: {e}")

# <emoji id='6181573775742472851'>🔥</emoji> THE MAGIC START FUNCTION — VIDEO VERSION
async def send_magic_start(chat_id, photo_url, caption, markup):
    try:
        token = getattr(config, "BOT_TOKEN", getattr(app, "bot_token", None))
        
        # Send photo
        url_api = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo_url if isinstance(photo_url, str) and photo_url.startswith("http") else "https://files.catbox.moe/ah5y0f.jpeg",
            "caption": caption,
            "parse_mode": "HTML",
            "has_spoiler": True,
            "message_effect_id": "5159385139981059251",
            "reply_markup": {"inline_keyboard": markup}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url_api, json=payload) as resp:
                res = await resp.json()
                if not res.get("ok"):
                    raise Exception("API rejected")
    except Exception as e:
        # Final fallback
        try:
            pic = random.choice(YUMI_PICS)
            run = await app.send_photo(chat_id, photo=pic, caption=caption, has_spoiler=True)
            await inject_premium_markup(chat_id, run.id, markup)
        except:
            pass


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    
    # <emoji id='6181573775742472851'>🔥</emoji> STEP 1: MESSAGE PE REACTION (<emoji id='6179125674448523622'>❤️</emoji>)
    try:
        await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="<emoji id='6179125674448523622'>❤️</emoji>")
    except: pass
        
    # <emoji id='6181573775742472851'>🔥</emoji> STEP 2: STICKER BHEJNA (less_than_es_by_fStikBot #18) + DELETE
    try:
        sticker_to_send = VENATRIX_STICKER_ID or "CAACAgUAAxkBAAFD0UBpqDbTjoP_CXF7Ce6oZykP4r64jQACxAcAArligFU4dyG-LQJBjDoE"
        stk = await message.reply_sticker(sticker_to_send)
        await asyncio.sleep(2) 
        await stk.delete()     
    except: pass

    # <emoji id='6181573775742472851'>🔥</emoji> STEP 3: LOADING ANIMATION
    loading_1 = await message.reply_text(random.choice(GREET))
    await add_served_user(message.from_user.id)
    
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='5219901967916084166'>😈</emoji> <b>ᴅɪηɢ ᴅᴏηɢ.</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='5219901967916084166'>😈</emoji> <b>ᴅɪηɢ ᴅᴏηɢ..</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='5219901967916084166'>😈</emoji> <b>ᴅɪηɢ ᴅᴏηɢ...</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='6179312501230932111'>😎</emoji> <b>sᴛᴧʀᴛɪηɢ.</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='6179312501230932111'>😎</emoji> <b>sᴛᴧʀᴛɪηɢ..</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='6179312501230932111'>😎</emoji> <b>sᴛᴧʀᴛɪηɢ...</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='6179275401303430193'>💖</emoji> <b>ʜєʏ ʙᴧʙʏ!</b>")
    await asyncio.sleep(0.1)
    await loading_1.edit_text("<emoji id='5222108309795908493'>🌺</emoji> <b>⋆ ˚｡⋆ Iᴢᴜᴍɪ ⋆｡˚ ⋆ ꭙ ϻᴜsɪᴄ ♪\nsᴛᴧʀᴛed!</b>")
    await asyncio.sleep(0.1)
    await loading_1.delete()
    
    # <emoji id='6181573775742472851'>🔥</emoji> STEP 4: FINAL START MESSAGE
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        
        # --- HELP COMMAND ---
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            try:
                run = await message.reply_photo(
                    random.choice(YUMI_PICS),
                    caption=_["help_1"].format(config.SUPPORT_CHAT),
                    message_effect_id=5159385139981059251, # <emoji id='6179125674448523622'>❤️</emoji> Hearts added here
                    has_spoiler=True  # 👈 Spoiler Here
                )
            except:
                run = await message.reply_photo(
                    random.choice(YUMI_PICS),
                    caption=_["help_1"].format(config.SUPPORT_CHAT),
                    has_spoiler=True  # 👈 Spoiler Here
                )
            return await inject_premium_markup(message.chat.id, run.id, keyboard)
            
        # --- SUDO LIST ---
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<blockquote><emoji id='6233067568878326937'>🐾</emoji> {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b><emoji id='5357592447557848986'>☠️</emoji> ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n<b><emoji id='6179286082887095182'>💀</emoji> ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}</blockquote>",
                )
            return
            
        # --- INFO COMMAND (HACKER SHIELD APPLIED) ---
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
                
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            
            key = [
                [
                    {"text": _["S_B_8"], "url": link, "style": "primary", "icon_custom_emoji_id": "5294017134756636818"},
                    {"text": _["S_B_9"], "url": config.SUPPORT_CHAT, "style": "danger", "icon_custom_emoji_id": "5357592447557848986"},
                ]
            ]
            await m.delete()
            
            # 🚨 HACKER SHIELD: Thumbnail bypass (ab hamesha teri catbox/safe pic hi aayegi)
            safe_thumbnail = "https://files.catbox.moe/i3w4v7.jpeg"
            
            # <emoji id='6181573775742472851'>🔥</emoji> Magic Start Call for Info (With Hearts Animation & Spoiler)
            await send_magic_start(
                chat_id=message.chat.id,
                photo_url=safe_thumbnail,
                caption=searched_text,
                markup=key
            )
            
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"<emoji id='6233067568878326937'>🐾</emoji> {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<emoji id='5357592447557848986'>☠️</emoji> <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n<emoji id='6179286082887095182'>💀</emoji> <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
                )
    else:
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        
        caption_text = _["start_2"].format(message.from_user.mention, app.mention, UP, DISK, CPU, RAM,served_users,served_chats)
        
        # <emoji id='6181573775742472851'>🔥</emoji> Normal Start Call (With Hearts Animation & Spoiler)
        await send_magic_start(
            chat_id=message.chat.id,
            photo_url=random.choice(YUMI_PICS),
            caption=caption_text,
            markup=out
        )
        
        if await is_on_off(2):
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<emoji id='6233067568878326937'>🐾</emoji> {message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<emoji id='5357592447557848986'>☠️</emoji> <b>ᴜsᴇʀ ɪᴅ ➠</b> <code>{message.from_user.id}</code>\n<emoji id='6179286082887095182'>💀</emoji> <b>ᴜsᴇʀɴᴀᴍᴇ ➠</b> @{message.from_user.username}",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    # <emoji id='6181573775742472851'>🔥</emoji> GROUP MEIN BHI REACTION AAYEGA
    try:
        await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="<emoji id='6179125674448523622'>❤️</emoji>")
    except: pass
    
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    
    # <emoji id='6181573775742472851'>🔥</emoji> GROUP MEIN HEARTS ANIMATION
    try:
        run = await message.reply_photo(
            random.choice(YUMI_PICS),
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            message_effect_id=5159385139981059251, # <emoji id='6179125674448523622'>❤️</emoji> Hearts effect
            has_spoiler=True # 👈 Spoiler Here
        )
    except:
        run = await message.reply_photo(
            random.choice(YUMI_PICS),
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            has_spoiler=True # 👈 Spoiler Here
        )
    await inject_premium_markup(message.chat.id, run.id, out)

@app.on_message(filters.command("promo") & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_photo(
        random.choice(YUMI_PICS),
        caption=PROMO,
        has_spoiler=True # 👈 Spoiler Here
    )

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
            
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                bot_welcome = f"<emoji id='6179312501230932111'>😎</emoji> <b>𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝖳𝗈 {message.chat.title}</b>\n<emoji id='6179275401303430193'>💖</emoji> 𝖳𝗁𝖺𝗇𝗄𝗌 𝖿𝗈𝗋 𝖺𝖽𝖽𝗂𝗇𝗀 𝗆𝖾, 𝖨 𝖺𝗆 𝗋𝖾𝖺𝖽𝗒 𝗍𝗈 𝗉𝗅𝖺𝗒!"
                
                run = await message.reply_text(text=bot_welcome, disable_web_page_preview=True)
                await inject_premium_markup(message.chat.id, run.id, out)
                
                await add_served_chat(message.chat.id)
                
                async def delete_bot_msg():
                    await asyncio.sleep(10)
                    try: await run.delete()
                    except: pass
                asyncio.create_task(delete_bot_msg())
                
                await message.stop_propagation()
            else:
                user_welcome = f"<emoji id='5222108309795908493'>🌺</emoji> <b>𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝖳𝗈 {message.chat.title}, {member.mention}!</b>"
                run = await message.reply_text(text=user_welcome, disable_web_page_preview=True)
                
                async def delete_user_msg():
                    await asyncio.sleep(10)
                    try: await run.delete()
                    except: pass
                asyncio.create_task(delete_user_msg())

        except Exception as ex:
            pass
            
