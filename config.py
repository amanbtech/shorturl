import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEYenv")
ALGORITHMS = os.getenv("ALGORITHMSenv")

REDIS_HOST = os.getenv("hostenv")
REDIS_PORT = int(os.getenv("portenv", "6379"))
REDIS_PASSWORD = os.getenv("passwordenv")
REDIS_USERNAME = os.getenv("usernameenv")

DATABASE_URL = "project1.db"