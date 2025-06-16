# repositories.py

import sqlite3
from typing import List, Optional
from models import User, Item, ChatMessage


class Database:
    """
    SQLite 연결을 관리하는 싱글톤 클래스.
    .get_connection()을 통해 항상 같은 DB 파일에 연결된다.
    """
    _instance = None
    _db_path  = 'used_market.db'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn


class UserRepository:
    """
    users 테이블 CRUD를 담당.
    """
    def __init__(self):
        self.db = Database()

    def create(self, email: str, password: str) -> Optional[int]:
        conn = self.db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            user_id = cur.lastrowid
        except sqlite3.IntegrityError:
            conn.close()
            return None
        conn.close()
        return user_id

    def find_by_email(self, email: str) -> Optional[User]:
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        if row:
            return User(id=row['id'], email=row['email'], password=row['password'])
        return None

    def find_by_id(self, user_id: int) -> Optional[User]:
        conn = self.db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return User(id=row['id'], email=row['email'], password=row['password'])
        return None


class ItemRepository:
    """
    items 테이블 CRUD를 담당.
    """
    def __init__(self):
        self.db = Database()

    def create(self, category: str, title: str, description: str, price: str, owner_id: int) -> int:
        conn = self.db.get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO items (category, title, description, price, owner_id) VALUES (?, ?, ?, ?, ?)",
            (category, title, description, price, owner_id)
        )
        conn.commit()
        item_id = cur.lastrowid
        conn.close()
        return item_id

    def find_all(self, search: str = "") -> List[Item]:
        conn = self.db.get_connection()
        cur  = conn.cursor()
        if search:
            pattern = f"%{search}%"
            cur.execute(
                "SELECT * FROM items WHERE title LIKE ? OR description LIKE ? ORDER BY id DESC",
                (pattern, pattern)
            )
        else:
            cur.execute("SELECT * FROM items ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            item = Item(
                id=row['id'],
                category=row['category'],
                title=row['title'],
                description=row['description'],
                price=row['price'],
                owner_id=row['owner_id']
            )
            result.append(item)
        return result

    def find_by_id(self, item_id: int) -> Optional[Item]:
        conn = self.db.get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Item(
                id=row['id'],
                category=row['category'],
                title=row['title'],
                description=row['description'],
                price=row['price'],
                owner_id=row['owner_id']
            )
        return None


class ChatRepository:
    """
    chat_messages 테이블 CRUD를 담당.
    (item_id 기준으로 채팅 메시지를 저장/조회)
    """
    def __init__(self):
        self.db = Database()

    def create(self, item_id: int, sender_id: int, message: str, timestamp: str) -> int:
        conn = self.db.get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO chat_messages (item_id, sender_id, message, timestamp) VALUES (?, ?, ?, ?)",
            (item_id, sender_id, message, timestamp)
        )
        conn.commit()
        msg_id = cur.lastrowid
        conn.close()
        return msg_id

    def find_by_item(self, item_id: int) -> List[ChatMessage]:
        conn = self.db.get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM chat_messages WHERE item_id = ? ORDER BY timestamp ASC", (item_id,))
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            msg = ChatMessage(
                id=row['id'],
                item_id=row['item_id'],
                sender_id=row['sender_id'],
                message=row['message'],
                timestamp=row['timestamp']
            )
            result.append(msg)
        return result
