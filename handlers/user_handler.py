"""
User Handler for managing user-related operations
"""
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
import re


@dataclass
class User:
    """Represents a connected user."""
    socket_id: str
    username: str
    display_name: str
    connected_at: datetime = field(default_factory=datetime.now)
    status: str = 'online'
    current_room: str = 'general'
    ip_address: str = 'unknown'
    
    def to_dict(self) -> dict:
        return {
            'socket_id': self.socket_id,
            'username': self.username,
            'display_name': self.display_name,
            'status': self.status,
            'current_room': self.current_room
        }


class UserHandler:
    """Handles user management and operations."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self._users: Dict[str, User] = {}
        self._usernames: Dict[str, str] = {}
        self._user_counter = 1
    
    def register_user(self, socket_id: str, username: str, ip: str = 'unknown') -> User:
        display_name = f"user{self._user_counter} ({username})"
        self._user_counter += 1
        
        user = User(socket_id=socket_id, username=username, display_name=display_name, ip_address=ip)
        self._users[socket_id] = user
        self._usernames[display_name] = socket_id
        
        if self.logger:
            self.logger.log_connection(socket_id, display_name, 'register', ip)
        return user
    
    def unregister_user(self, socket_id: str) -> Optional[User]:
        if socket_id not in self._users:
            return None
        user = self._users.pop(socket_id)
        self._usernames.pop(user.display_name, None)
        if self.logger:
            self.logger.log_connection(socket_id, user.display_name, 'disconnect')
        return user
    
    def get_user(self, socket_id: str) -> Optional[User]:
        return self._users.get(socket_id)
    
    def get_socket_id_by_username(self, username: str) -> Optional[str]:
        return self._usernames.get(username)
    
    def get_username(self, socket_id: str) -> Optional[str]:
        user = self._users.get(socket_id)
        return user.display_name if user else None
    
    def get_user_list(self) -> List[str]:
        return [user.display_name for user in self._users.values()]
    
    def user_count(self) -> int:
        return len(self._users)
