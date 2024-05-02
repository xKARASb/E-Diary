from .learner import Learner
from os import getenv
from dotenv import load_dotenv

load_dotenv()

JSESSIONID = getenv('JSESSIONID')
learner_client = Learner(JSESSIONID)
