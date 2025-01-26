# File: botDB.py
import sqlite3

def setup_database():
    conn = sqlite3.connect("malumotlar.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        timezone TEXT,
        phone_number TEXT
    )''')

    conn.commit()
    conn.close()