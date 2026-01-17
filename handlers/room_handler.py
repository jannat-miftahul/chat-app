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
    
    def leave_room(self, room_id: str, user_id: str, username: str) -> dict:
        """
        Handle room leave request.
        
        Args:
            room_id: ID of the room to leave
            user_id: Socket ID of the user
            username: User's display name
            
        Returns:
            Response dictionary with success status
        """
        try:
            success = self.room_service.leave_room(room_id, user_id, username)
            
            if success:
                self.logger.log_room_event(room_id, username, 'leave')
            
            return {
                'success': success,
                'room_id': room_id,
                'message': f"Left room" if success else "Failed to leave room"
            }
            
        except Exception as e:
            self.logger.error(f"Error leaving room: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    def delete_room(self, room_id: str, username: str) -> dict:
        """
        Handle room deletion request.
        
        Args:
            room_id: ID of the room to delete
            username: Requester's username
            
        Returns:
            Response dictionary with success status
        """
        try:
            success = self.room_service.delete_room(room_id, username)
            
            if success:
                self.logger.log_room_event(room_id, username, 'delete')
            
            return {
                'success': success,
                'room_id': room_id,
                'message': 'Room deleted successfully'
            }
            
        except RoomError as e:
            self.logger.warning(f"Room deletion failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Error deleting room: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    def get_rooms(self, include_private: bool = False) -> dict:
        """
        Get list of available rooms.
        
        Args:
            include_private: Whether to include private rooms
            
        Returns:
            Response dictionary with room list
        """
        try:
            rooms = self.room_service.get_all_rooms(include_private)
            return {
                'success': True,
                'rooms': rooms,
                'count': len(rooms)
            }
        except Exception as e:
            self.logger.error(f"Error getting rooms: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    def get_room_info(self, room_id: str) -> dict:
        """
        Get detailed information about a room.
        
        Args:
            room_id: ID of the room
            
        Returns:
            Response dictionary with room info
        """
        try:
            room = self.room_service.get_room(room_id)
            
            if room:
                return {
                    'success': True,
                    'room': room.to_dict()
                }
            else:
                return {'success': False, 'error': 'Room not found'}
                
        except Exception as e:
            self.logger.error(f"Error getting room info: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    def get_room_members(self, room_id: str) -> dict:
        """
        Get list of members in a room.
        
        Args:
            room_id: ID of the room
            
        Returns:
            Response dictionary with member list
        """
        try:
            members = self.room_service.get_room_members(room_id)
            return {
                'success': True,
                'room_id': room_id,
                'members': members,
                'count': len(members)
            }
        except Exception as e:
            self.logger.error(f"Error getting room members: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'An unexpected error occurred'}
    
    def handle_disconnect(self, user_id: str, username: str) -> list:
        """
        Handle user disconnect - leave all rooms.
        
        Args:
            user_id: Socket ID of the user
            username: User's display name
            
        Returns:
            List of room IDs the user left
        """
        try:
            left_rooms = self.room_service.leave_all_rooms(user_id, username)
            
            for room_id in left_rooms:
                self.logger.log_room_event(room_id, username, 'disconnect')
            
            return left_rooms
            
        except Exception as e:
            self.logger.error(f"Error handling disconnect: {str(e)}", exc_info=True)
            return []
