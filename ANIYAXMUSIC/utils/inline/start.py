import config
from ANIYAXMUSIC import app

# <emoji id='6181573775742472851'>🔥</emoji> HELLFIRE DEVS HACK: Raw API Button Generator (Fixed for Telegram Limits)
def api_btn(text, callback_data=None, url=None, style=None, custom_emoji_id=None):
    btn = {"text": text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        url_str = str(url)
        if not url_str.startswith("http") and not url_str.startswith("tg://"):
            url_str = f"https://t.me/{url_str.replace('@', '')}"
        btn["url"] = url_str
        
    # <emoji id='6181573775742472851'>🔥</emoji> FIX: Sirf Valid Telegram Styles Allow Karenge!
    if style in ["primary", "danger", "success"]:
        btn["style"] = style  
        
    if custom_emoji_id:
        btn["icon_custom_emoji_id"] = str(custom_emoji_id) 
    return btn


def start_panel(_):
    buttons = [
        [
            # Add to Group (Blue)
            api_btn(
                text=_["S_B_1"], 
                url=f"https://t.me/{app.username}?startgroup=true", 
                style="success", 
                custom_emoji_id="5454365405130810498"
            ),
            # Support Chat (Red)
            api_btn(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT, 
                style="danger", 
                custom_emoji_id="5357592447557848986"
            ),
        ],
    ]
    return buttons


def private_panel(_):
    safe_owner_id = config.OWNER_ID[0] if isinstance(config.OWNER_ID, list) else config.OWNER_ID
    
    buttons = [
        [
            # Add to Group (Blue)
            api_btn(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style="success",
                custom_emoji_id="5294017134756636818"
            )
        ],
        [
            # Settings/Help (<emoji id='6181573775742472851'>🔥</emoji> GREEN banaya isko taaki crash na ho)
            api_btn(
                text=_["S_B_4"], 
                callback_data="settings_back_helper", 
                style="primary", 
                custom_emoji_id="5244820603663296299"
            ),
            # Balling button
            api_btn(
                text="𝚩𝛂𝛏𝛏𝛊𝛏𝛄", 
                url="https://t.me/Imm_ShizukaBot", 
                style="primary", 
                custom_emoji_id="5222108309795908493"
            ),
        ],
        [
            # Updates/Channel (Blue)
            api_btn(
                text=_["S_B_6"], 
                url=config.SUPPORT_CHANNEL, 
                style="primary", 
                custom_emoji_id="5219943216781995020"
            ),
            # Support Chat (Red)
            api_btn(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT, 
                style="danger", 
                custom_emoji_id="5357592447557848986"
            ),
        ],
        [
            # Owner (Red)
            api_btn(
                text=_["S_B_5"], 
                url=f"tg://user?id={safe_owner_id}", 
                style="danger", 
                custom_emoji_id="5219901967916084166"
            ),
        ],
    ]
    return buttons
    
