#okay


#mil gaya 

import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ANIYAXMUSIC import LOGGER, app, userbot
from ANIYAXMUSIC.core.call import ANIYA
from ANIYAXMUSIC.misc import sudo
from ANIYAXMUSIC.plugins import ALL_MODULES
from ANIYAXMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

async def _fetch_sticker_on_start():
    try:
        from ANIYAXMUSIC.plugins.bot.start import fetch_venatrix_sticker
        await fetch_venatrix_sticker()
        LOGGER("ANIYAXMUSIC").info("Venatrix sticker #18 fetched successfully!")
    except Exception as e:
        LOGGER("ANIYAXMUSIC").warning(f"Sticker fetch skipped: {e}")


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("𝐒𝐭𝐫𝐢𝐧𝐠 𝐒𝐞𝐬𝐬𝐢𝐨𝐧 𝐍𝐨𝐭 𝐅𝐢𝐥𝐥𝐞𝐝, 𝐏𝐥𝐞𝐚𝐬𝐞 𝐅𝐢𝐥𝐥 𝐀 𝐏𝐲𝐫𝐨𝐠𝐫𝐚𝐦 𝐒𝐞𝐬𝐬𝐢𝐨𝐧")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ANIYAXMUSIC.plugins" + all_module)
    LOGGER("ANIYAXMUSIC.plugins").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")
    await userbot.start()
    await ANIYA.start()
    try:
        await ANIYA.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ANIYAXMUSIC").warning(
            "Log group mein voice chat active nahi hai - bot phir bhi chal raha hai!"
        )
    except Exception:
        pass
    await ANIYA.decorators()
    await _fetch_sticker_on_start()
    LOGGER("ANIYAXMUSIC").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎𝗠𝗔𝗗𝗘 𝗕𝗬 ⋆ ˚｡⋆ Iᴢᴜᴍɪ ⋆｡˚ ⋆\n╚═════ஜ۩۞۩ஜ════╝"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("ANIYAXMUSIC").info("𝗦𝗧𝗢𝗣 ⋆ ˚｡⋆ Iᴢᴜᴍɪ ⋆｡˚ ⋆ 𝗠𝗨𝗦𝗜𝗖🎻 𝗕𝗢𝗧..")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
