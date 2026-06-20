from ANIYAXMUSIC.core.bot import ANIYA
from ANIYAXMUSIC.core.dir import dirr
from ANIYAXMUSIC.core.git import git
from ANIYAXMUSIC.core.userbot import Userbot
from ANIYAXMUSIC.misc import dbb, heroku

from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
dbb()
heroku()

app = ANIYA()
userbot = Userbot()
api = SafoneAPI()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

APP = "ll_DRAGON_MUSIC_BOT"  # connect music api key "Dont change it"
