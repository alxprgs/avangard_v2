import uvicorn
from web import app 
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    try:
        load_dotenv()
        uvicorn.run("web:app", port=int(os.getenv("port")), host="0.0.0.0", reload=True)
    except Exception as e:
        print(f"error: {e}")