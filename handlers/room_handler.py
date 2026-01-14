"""
Room Handler for managing room-related socket events
"""
from typing import Optional
from services.rooms import RoomService, RoomError
from services.logger import LoggerService


class RoomHandler:
    """
    Handles room-related socket events and operations.
    
    Features:
    - Room creation and deletion
    - User join/leave management
    - Room listing and info
    - Room message broadcasting
    """
    
    def __init__(self, room_service: RoomService, logger: LoggerService):
        """
        Initialize the room handler.
        
        Args:
            room_service: Instance of RoomService
            logger: Instance of LoggerService
        """
        self.room_service = room_service
        self.logger = logger
    
    def create_room(self, room_data: dict, username: str) -> dict:
        """
        Handle room creation request.
        
        Args:
            room_data: Dictionary with room_id, name, is_private, description
            username: Creator's username
            
        Returns:
            Response dictionary with success status and room info
        """
        try:
            room_id = room_data.get('room_id', '').lower().replace(' ', '-')
            name = room_data.get('name', room_id)
            is_private = room_data.get('is_private', False)
            description = room_data.get('description', '')
            max_users = room_data.get('max_users', 50)
            
            if not room_id:
                return {'success': False, 'error': 'Room ID is required'}
            
            room = self.room_service.create_room(
                room_id=room_id,
                name=name,
                created_by=username,
                is_private=is_private,
                max_users=max_users,
                description=description
            )
            
            self.logger.log_room_event(room_id, username, 'create')
            
            return {
                'success': True,
                'room': room.to_dict(),
                'message': f"Room '{name}' created successfully"
            }
            
        except RoomError as e:
            self.logger.warning(f"Room creation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error creating room: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    def join_room(self, room_id: str, user_id: str, username: str) -> dict:
        """
        Handle room join request.
        
        Args:
            room_id: ID of the room to join
            user_id: Socket ID of the user
            username: User's display name
            
        Returns:
            Response dictionary with success status
        """
        try:
            room = self.room_service.join_room(room_id, user_id, username)
            
            # Get message history for the room
            history = self.room_service.get_message_history(room_id, limit=50)
            
            self.logger.log_room_event(room_id, username, 'join')
            
            return {
                'success': True,
                'room': room.to_dict(),
                'history': history,
                'message': f"Joined room '{room.name}'"
            }
            
        except RoomError as e:
            self.logger.warning(f"Room join failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error joining room: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    