import pymongo
from fastapi import *
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from aiogram import Bot
from aiogram.types import ParseMode

load_dotenv()
app = FastAPI(version="Beta 1.0 | Build 23.10.2024",
              debug=True,)


try:
    client = pymongo.MongoClient(os.getenv("MONGO_URL"))
    database = client["avangard"]
except Exception as e:
    print(f"Ошибка подключения к базе данных: {str(e)}")
    raise e

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

from web.routes import message, chats, code_check, create_user, messages, root
