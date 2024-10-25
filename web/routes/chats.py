from web import database, app
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from web.functions import *

@app.get("/chat_list")
async def get_chat_list(authcode: str):
    try:
        user = database["users"].find_one({
            "auth_code": authcode
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    if user:
        return JSONResponse(content=user["chats"], status_code=200)
    else:
        return JSONResponse({"status": False, "message": "Неверный код доступа."})