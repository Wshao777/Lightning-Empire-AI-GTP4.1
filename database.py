import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('private_core/memory.db')
conn.execute('''CREATE TABLE IF NOT EXISTS interactions 
                (id INTEGER PRIMARY KEY, timestamp TEXT, model TEXT, prompt TEXT, response TEXT, feedback TEXT)''')

def log_interaction(model, prompt, response, feedback=""):
    conn.execute("INSERT INTO interactions VALUES (NULL, ?, ?, ?, ?, ?)",
                 (datetime.now().isoformat(), model, prompt, response, feedback))
    conn.commit()

def get_recent_memory(limit=10):
    cur = conn.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
    return cur.fetchall()
