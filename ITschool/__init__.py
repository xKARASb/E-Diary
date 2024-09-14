from .learner import Learner
from os import getenv
from dotenv import load_dotenv

load_dotenv()

ESIA_PASSWORD = getenv('ESIA-PASSWORD')
ESIA_LOGIN= getenv('ESIA-LOGIN')
ESIA_TOTP = getenv('ESIA-TOTP-KEY')
BOT_TOKEN = getenv('BOT-TOKEN')
USER_ID = getenv('USER-ID')
learner_client = Learner(
    bot_token=BOT_TOKEN,
    notification_user_id=USER_ID,
    esia_login=ESIA_LOGIN,
    esia_password=ESIA_PASSWORD,
    esia_totp_key=ESIA_TOTP
    )
