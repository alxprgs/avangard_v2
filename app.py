from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ContentType
from aiogram.utils import executor
import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

client = AsyncIOMotorClient(MONGO_URL)
db = client['avangard']
chats_collection = db['chats']
messages_collection = db['messages']

user_data = {
    "tg_id": None,
    "nickname": None,
    "phone_number": None,
    "chats": []
}

async def get_chat_ids(user_id):
    chat_ids = []
    chats = chats_collection.find({})

    async for chat in chats:
        chat_id = chat['chat_id_tg']
        users = chat['users']

        if str(user_id) in [str(uid) for uid in users.values()]:
            chat_ids.append(chat_id)
    
    return chat_ids

async def check_group_id(id):
    return bool(await db["chats"].find_one({"chat_id_tg": id}))

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_data = {
        'tg_id': message.from_user.id,
        'nickname': message.from_user.username
    }

    try:
        user_data['chats'] = await get_chat_ids(user_data['tg_id'])
    except Exception as e:
        print("Ошибка при получении идентификаторов чатов:", e)

    server_url = f"http://194.67.67.45:5001/user_create?tg_id={user_data['tg_id']}&nickname={quote_plus(user_data['nickname'])}"

    for chat_id in user_data['chats']:
        server_url += f"&chats={chat_id}"

    try:
        if user_data['chats']:
            response = requests.get(server_url)
            if response.status_code == 200:
                data = response.json()
                auth_code = data.get("auth_code")
                await message.answer(f"Данные успешно отправлены на сервер. Код доступа: <pre>{auth_code}</pre>", parse_mode="HTML")
            else:
                await message.answer(f"Ошибка при отправке данных на сервер: {response.status_code}")
        else:
            await message.answer("У вас нет чатов для отправки.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке данных: {e}")


@dp.message_handler(content_types=ContentType.NEW_CHAT_MEMBERS)
async def new_chat_member_handler(message: types.Message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.id:
            chat_name = message.chat.title
            chat_id_tg = message.chat.id
            server_chat_id = await chats_collection.count_documents({}) + 1

            users = {}
            try:
                administrators = await bot.get_chat_administrators(chat_id_tg)
                for admin in administrators:
                    user_id = admin.user.id
                    user_name = f"@{admin.user.username}" if admin.user.username else admin.user.full_name
                    users[user_name] = user_id
            except Exception as e:
                print(f"Ошибка при получении данных администратора: {e}")

            new_chat_data = {
                "chat_name": chat_name,
                "chat_id_tg": chat_id_tg,
                "server_chat_id": server_chat_id,
                "users": users
            }

            await chats_collection.insert_one(new_chat_data)
            print(f"Бот добавлен в новый чат: {chat_name} (ID: {chat_id_tg})")
            await message.answer(f"Успешная запись в базу данных.")

@dp.message_handler(commands=['update'])
async def update_chat_data(message: types.Message):
    chat_name = message.chat.title
    chat_id_tg = message.chat.id
    server_chat_id = await chats_collection.count_documents({}) + 1

    users = {}
    try:
        members = await bot.get_chat_administrators(chat_id_tg)
        for member in members:
            user_id = member.user.id
            user_name = f"@{member.user.username}" if member.user.username else member.user.full_name
            users[user_name] = user_id
    except Exception as e:
        print(f"Ошибка при получении данных администратора: {e}")

    new_chat_data = {
        "chat_name": chat_name,
        "chat_id_tg": chat_id_tg,
        "server_chat_id": server_chat_id,
        "users": users
    }

    existing_chat = await chats_collection.find_one({"chat_id_tg": chat_id_tg})
    if existing_chat:
        await chats_collection.update_one(
            {"chat_id_tg": chat_id_tg},
            {"$set": new_chat_data}
        )
    else:
        await chats_collection.insert_one(new_chat_data)

    print(f"Данные о чате обновлены: {chat_name} (ID: {chat_id_tg})")
    await message.answer("Данные чата успешно обновлены в базе данных.")





@dp.message_handler(content_types=types.ContentType.TEXT)
async def text_message_handler(message: types.Message):
    
    if await check_group_id(message.chat.id):
        authorbot = message.from_user.id == bot.id

        internal_id = await messages_collection.count_documents({})  

        message_data = {
            "internal_id": internal_id,  
            "timestamp": datetime.now().isoformat(),
            "author": message.from_user.username,
            "message": message.text,
            "authorbot": authorbot,  
            "message_id": message.message_id,
            "server_id": message.chat.id
        }

        await messages_collection.insert_one(message_data)

        print("Сообщение сохранено:", message_data)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
