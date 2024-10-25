from web import bot, database, app
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import *
from web.functions import *
import datetime

def db_insert(nick, message, server_id):
    try:
        internal_id = database["messages"].count_documents({})
        database["messages"].insert_one({
            "internal_id": internal_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "author": nick,
            "message": message,
            "authorbot": True,
            "message_id": None,
            "server_id": server_id
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@app.get("/message")
async def send_message(
    authcode: int = Query(...),
    message: str = Query(...),
    chat_id: int = Query(...),
    nick: str = Query(None),
    return_link: str = Query(...)
):
    print(chat_id)
    print(f"Received: authcode={authcode}, message={message}, chat_id={chat_id}, nick={nick}")
    print(f"Auth code 1: {authcode}")
    try:
        user = database["users"].find_one({"auth_code": authcode})
        print(f"Auth code 3: {authcode}")
        if user:
            if message:
                if nick is None:
                    nick = user["nickname"]

                db_insert(nick=nick, message=message, server_id=chat_id)

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
                message_text = f"Сообщение от {nick}; \nВремя отправки {timestamp}; \nСообщение:\n{message}"
                await bot.send_message(chat_id=chat_id, text=message_text)
                await bot.close()
                
                return RedirectResponse(url=return_link)
            else:
                return JSONResponse({"status": False, "message": "Пустое сообщение."})
        else:
            return JSONResponse({"status": False, "message": "Неверный код доступа."})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
