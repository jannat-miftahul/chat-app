"""
Room Service for managing chat rooms
Handles room creation, user management, and room-specific features
"""
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Room:
    """Represents a chat room."""
    id: str
    name: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    is_private: bool = False
    max_users: int = 50
    description: str = ""
    members: Set[str] = field(default_factory=set)
    admins: Set[str] = field(default_factory=set)
    message_history: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert room to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'is_private': self.is_private,
            'max_users': self.max_users,
            'description': self.description,
            'member_count': len(self.members),
            'members': list(self.members),
            'admins': list(self.admins)
        }


class RoomService:
    """
    Manages chat rooms and room-related operations.
    
    Features:
    - Create and delete rooms
    - Join and leave rooms
    - Room access control (private/public)
    - Room administration
    - Message history per room
    """
    
    def __init__(self, default_room: str = 'General', history_limit: int = 100):
        """
        Initialize the room service.
        
        Args:
            default_room: Name of the default room all users join
            history_limit: Maximum number of messages to store per room
        """
        self._rooms: Dict[str, Room] = {}
        self._user_rooms: Dict[str, Set[str]] = {}  # user_id -> set of room_ids
        self._history_limit = history_limit
        
        # Create default room
        self.create_room(
            room_id='general',
            name=default_room,
            created_by='System',
            description='Welcome to the general chat room!'
        )
    
    def create_room(self, room_id: str, name: str, created_by: str,
                    is_private: bool = False, max_users: int = 50,
                    description: str = "") -> Room:
        """
        Create a new chat room.
        
        Args:
            room_id: Unique identifier for the room
            name: Display name of the room
            created_by: Username of the creator
            is_private: Whether the room is private
            max_users: Maximum number of users allowed
            description: Room description
            
        Returns:
            The created Room object
            
        Raises:
            RoomError: If room already exists
        """
        if room_id in self._rooms:
            raise RoomError(f"Room '{room_id}' already exists")
        
        room = Room(
            id=room_id,
            name=name,
            created_by=created_by,
            is_private=is_private,
            max_users=max_users,
            description=description
        )
        
        # Creator is automatically an admin
        room.admins.add(created_by)
        
        self._rooms[room_id] = room
        return room
    
    def delete_room(self, room_id: str, requested_by: str) -> bool:
        """
        Delete a chat room.
        
        Args:
            room_id: ID of the room to delete
            requested_by: Username requesting deletion
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            RoomError: If room doesn't exist or user lacks permission
        """
        if room_id == 'general':
            raise RoomError("Cannot delete the default room")
        
        if room_id not in self._rooms:
            raise RoomError(f"Room '{room_id}' does not exist")
        
        room = self._rooms[room_id]
        
        if requested_by not in room.admins and requested_by != room.created_by:
            raise RoomError("Only room admins can delete the room")
        
        # Remove room from all users
        for user_id in list(self._user_rooms.keys()):
            self._user_rooms[user_id].discard(room_id)
        
        del self._rooms[room_id]
        return True
    
    def join_room(self, room_id: str, user_id: str, username: str) -> Room:
        """
        Add a user to a room.
        
        Args:
            room_id: ID of the room to join
            user_id: Socket ID of the user
            username: Display name of the user
            
        Returns:
            The Room object
            
        Raises:
            RoomError: If room doesn't exist or is full
        """
        if room_id not in self._rooms:
            raise RoomError(f"Room '{room_id}' does not exist")
        
        room = self._rooms[room_id]
        
        if len(room.members) >= room.max_users:
            raise RoomError(f"Room '{room.name}' is full")
        
        room.members.add(username)
        
        if user_id not in self._user_rooms:
            self._user_rooms[user_id] = set()
        self._user_rooms[user_id].add(room_id)
        
        return room
    
    def leave_room(self, room_id: str, user_id: str, username: str) -> bool:
        """
        Remove a user from a room.
        
        Args:
            room_id: ID of the room to leave
            user_id: Socket ID of the user
            username: Display name of the user
            
        Returns:
            True if successfully left
        """
        if room_id not in self._rooms:
            return False
        
        room = self._rooms[room_id]
        room.members.discard(username)
        
        if user_id in self._user_rooms:
            self._user_rooms[user_id].discard(room_id)
        
        return True
    
    def leave_all_rooms(self, user_id: str, username: str) -> List[str]:
        """
        Remove a user from all rooms (on disconnect).
        
        Args:
            user_id: Socket ID of the user
            username: Display name of the user
            
        Returns:
            List of room IDs the user left
        """
        left_rooms = []
        
        if user_id in self._user_rooms:
            for room_id in list(self._user_rooms[user_id]):
                if room_id in self._rooms:
                    self._rooms[room_id].members.discard(username)
                    left_rooms.append(room_id)
            del self._user_rooms[user_id]
        
        return left_rooms
    
    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID."""
        return self._rooms.get(room_id)
    
    def get_all_rooms(self, include_private: bool = False) -> List[dict]:
        """
        Get all available rooms.
        
        Args:
            include_private: Whether to include private rooms
            
        Returns:
            List of room dictionaries
        """
        rooms = []
        for room in self._rooms.values():
            if include_private or not room.is_private:
                rooms.append(room.to_dict())
        return rooms
    
    def get_user_rooms(self, user_id: str) -> List[str]:
        """Get all room IDs a user is in."""
        return list(self._user_rooms.get(user_id, set()))
    
    def get_room_members(self, room_id: str) -> List[str]:
        """Get all members in a room."""
        if room_id not in self._rooms:
            return []
        return list(self._rooms[room_id].members)
    
    def add_message_to_history(self, room_id: str, message: dict) -> None:
        """
        Add a message to room's history.
        
        Args:
            room_id: ID of the room
            message: Message dictionary with sender, content, timestamp
        """
        if room_id not in self._rooms:
            return
        
        room = self._rooms[room_id]
        room.message_history.append(message)
        
        # Trim history if exceeds limit
        if len(room.message_history) > self._history_limit:
            room.message_history = room.message_history[-self._history_limit:]
    
    def get_message_history(self, room_id: str, limit: int = 50) -> List[dict]:
        """
        Get recent messages from a room.
        
        Args:
            room_id: ID of the room
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        if room_id not in self._rooms:
            return []
        
        messages = self._rooms[room_id].message_history
        return messages[-limit:] if limit else messages
    
    def is_user_in_room(self, room_id: str, username: str) -> bool:
        """Check if a user is in a specific room."""
        if room_id not in self._rooms:
            return False
        return username in self._rooms[room_id].members
    
    def make_admin(self, room_id: str, username: str, requested_by: str) -> bool:
        """
        Make a user an admin of a room.
        
        Args:
            room_id: ID of the room
            username: User to make admin
            requested_by: User requesting the change
            
        Returns:
            True if successful
        """
        if room_id not in self._rooms:
            raise RoomError(f"Room '{room_id}' does not exist")
        
        room = self._rooms[room_id]
        
        if requested_by not in room.admins:
            raise RoomError("Only admins can add other admins")
        
        room.admins.add(username)
        return True
    
    def room_count(self) -> int:
        """Get the total number of rooms."""
        return len(self._rooms)
    
    def total_users_in_rooms(self) -> int:
        """Get the total number of users across all rooms."""
        return sum(len(room.members) for room in self._rooms.values())


class RoomError(Exception):
    """Custom exception for room-related errors."""
    pass
