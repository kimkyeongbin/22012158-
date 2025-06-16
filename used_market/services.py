# services.py

from typing import Optional, List
from models import User, Item, Category, ChatRoom, ChatMessage
from repositories import UserRepository, ItemRepository, ChatRoomRepository, ChatMessageRepository
import datetime

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register(self, email: str, password: str) -> Optional[int]:
        return self.user_repo.create(email, password)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.find_by_email(email)
        if user and user.password == password:
            return user
        return None


class ItemService:
    def __init__(self):
        self.item_repo = ItemRepository()

    def register_item(self, category: str, title: str, description: str, price: str, owner_id: int) -> int:
        return self.item_repo.create(category, title, description, price, owner_id)

    def list_items(self, search: str = "") -> List[Item]:
        return self.item_repo.find_all(search)

    def get_item(self, item_id: int) -> Optional[Item]:
        return self.item_repo.find_by_id(item_id)


class ChatService:
    def __init__(self):
        self.room_repo    = ChatRoomRepository()
        self.message_repo = ChatMessageRepository()

    def get_or_create_room(self, item_id: int) -> ChatRoom:
        room = self.room_repo.find_by_item_id(item_id)
        if room:
            return room
        room_id = self.room_repo.create(item_id)
        return ChatRoom(id=room_id, item_id=item_id)

    def send_message(self, room_id: int, sender_id: int, message: str) -> int:
        timestamp = datetime.datetime.now().isoformat()
        return self.message_repo.create(room_id, sender_id, message, timestamp)

    def list_messages(self, room_id: int) -> List[ChatMessage]:
        return self.message_repo.find_by_room_id(room_id)
