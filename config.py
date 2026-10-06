import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.environ.get("DATABASE", os.path.join(BASE_DIR, "urls.db"))
SHORT_CODE_LENGTH = 6
MAX_URL_LENGTH = 2048
