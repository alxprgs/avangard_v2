from web import database, app
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse
from web.functions import generate_unique_code

@app.get("/user_create")
async def user_create(tg_id: int, nickname: str, chats: list[int] = Query(...)):
    try:
        user = database["users"].find_one({
            "tg_id": tg_id
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    
    if user:
        return JSONResponse({"status": False, "message": "Пользователь уже зарегистрирован."})
    else:
        auth_code = int(generate_unique_code())
        print(auth_code)
        user = database["users"].insert_one({
            "tg_id": tg_id,
            "nickname": nickname,
            "auth_code": auth_code,
            "chats": chats
        })
        return JSONResponse({"status": True, "message": "Пользователь успешно создан.", "auth_code": auth_code})
