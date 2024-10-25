from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pymongo import DESCENDING
from fastapi.staticfiles import StaticFiles
from web import database, app

@app.get("/chat", response_class=HTMLResponse)
async def chat(authcode: int, grup_id: int):
    user = database["users"].find_one({"auth_code": authcode})
    id_zxc = grup_id
    if user:

        messages_cursor = database["messages"].find({"server_id": grup_id}).sort("_id", DESCENDING).limit(100)
        
        messages = []
        
        for message in messages_cursor:
            author = message.get("author")
            msg = message.get("message", "Сообщение отсутствует")
            timestamp = message.get("timestamp", "")
            time_str = timestamp[11:16] if timestamp else "??:??"
            messages.append(f"<div><strong>{author}</strong>: {msg} <span style='font-size: small;'>{time_str}</span></div>")
        chat = database["chats"].find_one({"chat_id_tg": grup_id})
        print(chat)
        chat_name = chat["chat_name"]
        print(chat_name)
        messages = messages[::-1]
        
        messages_html = "".join(messages)
        link = (f"/chat/?authcode={authcode}&grup_id={id_zxc}")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">  
            <title>{chat_name}</title>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    font-family: Arial, sans-serif;     
                    display: flex; 
                    flex-direction: column; 
                    height: 100vh; 
                }}
                #messages {{ 
                    flex: 1; 
                    overflow-y: auto;  
                    padding: 5px; 
                    padding-bottom: 60px;
                    background-color: #f0f0f0;  
                    border: 1px solid #ccc;  
                    font-size: 12px;  
                }}
                #messageForm {{ 
                    display: flex;  
                    padding: 5px; 
                    background-color: #fff;
                    border-top: 1px solid #ccc;
                    position: fixed;
                    bottom: 0;
                    left: 0; 
                    right: 0; 
                }}
                input[type="text"] {{ 
                    width: 70%;  
                    font-size: 12px;  
                    padding: 5px;  
                    margin-right: 5px;
                }}
                button {{ 
                    font-size: 12px;  
                    padding: 5px;  
                }}  
                @media (min-width: 320px) {{ 
                    #messages, input[type="text"], button {{ 
                        font-size: 16px;  
                    }}
                }}
                @media (min-width: 480px) {{ 
                    #messages, input[type="text"], button {{ 
                        font-size: 18px;  
                    }}
                }}
            </style>
        </head>
        <body>
            <div id="messages">
                {messages_html}
            </div>
            <form id="messageForm" action="/message" method="GET">
                <input type="text" name="message" placeholder="Введите сообщение..." required>
                <input type="hidden" name="authcode" value="{authcode}">
                <input type="hidden" name="chat_id" value="{id_zxc}">
                <input type="hidden" name="return_link" value="{link}">
                <button type="submit">Отправить</button>
            </form>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)
    else:
        return JSONResponse({"status": False, "message": "Неверный код доступа"})
