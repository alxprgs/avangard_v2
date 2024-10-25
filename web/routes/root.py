from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pymongo import DESCENDING
from fastapi.staticfiles import StaticFiles
from web import database, app


@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>auth</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                margin: 0;
                padding: 10px;
                background-color: #f0f0f0;
                text-align: center;
            }}
            input, button {{
                width: 100%;
                font-size: 12px;
                margin-bottom: 5px;
            }}
        </style>
    </head>
    <body>
        <form id="messageForm" action="/hoice" method="GET">
            <input type="number" name="auth_code" placeholder="Код доступа" required>
            <button type="submit">Открыть</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/hoice/", response_class=HTMLResponse)
async def choise(auth_code: int):
    user = database["users"].find_one({
        "auth_code": auth_code
    })
    if user:
        chats = user["chats"]
        
        options = []
        for chat_id in chats:
            chat = database["chats"].find_one({"chat_id_tg": chat_id})
            if chat:
                chat_name = chat["chat_name"]
                options.append(f"<option value='{chat_id}'>{chat_name}</option>")
        
        options_html = "".join(options)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <title>Выбор</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    margin: 0;
                    padding: 10px;
                    background-color: #f0f0f0;
                    text-align: center;
                }}
                select, input[type="submit"] {{
                    width: 100%;
                    font-size: 12px;
                    margin-bottom: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>Выберите чат</h1>
            <form action="/chat" method="get">
                <input type="hidden" name="authcode" value="{auth_code}">
                <select name="grup_id">
                    {options_html}
                </select>
                <input type="submit" value="Открыть">
            </form>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        return RedirectResponse("/")
