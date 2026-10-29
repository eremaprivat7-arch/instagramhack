# python, backend/db.py
import sqlite3
import os

# База данных всегда создается рядом с файлом db.py, независимо от того, откуда запущен скрипт
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'creds.db')

def init():
    # check_same_thread=False нужен для FastAPI, чтобы база не блокировалась при параллельных запросах
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS hits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, password TEXT, ip TEXT, ua TEXT,
        valid INTEGER DEFAULT 0, ts INTEGER)""")
    c.commit()
    return c