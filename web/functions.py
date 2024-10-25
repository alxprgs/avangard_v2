import random
import os
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.utils.exceptions import ChatNotFound
from typing import List
import asyncio

def generate_unique_code(length=10):
    digits = list('0123456789')
    
    random.shuffle(digits)
    
    code = ''.join(digits[:length])
    
    return code

async def get_group_messages(tg_id_group: int) -> List[str]:
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    result = []

    async with Bot(token=BOT_TOKEN) as bot:
        try:
            updates = await bot.get_updates()

            for update in updates:
                if update.message and update.message.chat.id == tg_id_group:
                    message = update.message
                    if message.from_user.is_bot:
                        formatted_message = f"{message.from_user.username}: {message.text}"
                    else:
                        formatted_message = f"{message.from_user.first_name}: {message.text}"

                    result.append(formatted_message)

        except ChatNotFound:
            result.append(f"Чат с ID {tg_id_group} не найден.")
    
    return result

if __name__ == "__main__":
    messages = asyncio.run(get_group_messages(tg_id_group=-1002329147453))
    print(messages)
