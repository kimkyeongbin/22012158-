# db.py

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('used_market.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur  = conn.cursor()

    # users 테이블
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        email    TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    ''')

    # items 테이블
    cur.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        category    TEXT NOT NULL,
        title       TEXT NOT NULL,
        description TEXT,
        price       TEXT NOT NULL,
        owner_id    INTEGER NOT NULL,
        FOREIGN KEY(owner_id) REFERENCES users(id)
    );
    ''')

    # chat_messages 테이블
    cur.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id    INTEGER NOT NULL,
        sender_id  INTEGER NOT NULL,
        message    TEXT NOT NULL,
        timestamp  TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id),
        FOREIGN KEY(sender_id) REFERENCES users(id)
    );
    ''')

    conn.commit()
    conn.close()
