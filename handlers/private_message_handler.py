"""
Private Message Handler for direct messaging between users
"""
from datetime import datetime
from typing import Dict, List, Optional
import time


class PrivateMessageHandler:
    """Handles private/direct messaging between users."""
    
    def __init__(self, encryption_service=None, logger=None):
        self.encryption = encryption_service
        self.logger = logger
        self._conversations: Dict[str, List[dict]] = {}
        self._history_limit = 100
    
    def _get_conversation_id(self, user1: str, user2: str) -> str:
        """Generate consistent conversation ID for two users."""
        users = sorted([user1, user2])
        return f"dm_{users[0]}_{users[1]}"
    
    def send_message(self, sender: str, receiver: str, content: str, encrypt: bool = True) -> dict:
        """Send a private message."""
        conv_id = self._get_conversation_id(sender, receiver)
        
        # Encrypt if enabled
        if encrypt and self.encryption:
            try:
                content = self.encryption.encrypt(content)
            except Exception:
                encrypt = False
        
        message = {
            'id': f"pm_{int(time.time() * 1000)}",
            'sender': sender,
            'receiver': receiver,
            'content': content,
            'encrypted': encrypt,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        # Store in history
        if conv_id not in self._conversations:
            self._conversations[conv_id] = []
        self._conversations[conv_id].append(message)
        
        # Trim history
        if len(self._conversations[conv_id]) > self._history_limit:
            self._conversations[conv_id] = self._conversations[conv_id][-self._history_limit:]
        
        if self.logger:
            self.logger.log_private_message(sender, receiver)
        
        return message
    
    def get_conversation(self, user1: str, user2: str, limit: int = 50) -> List[dict]:
        """Get conversation history between two users."""
        conv_id = self._get_conversation_id(user1, user2)
        messages = self._conversations.get(conv_id, [])
        return messages[-limit:]
    
    def decrypt_message(self, message: dict) -> dict:
        """Decrypt a private message."""
        if message.get('encrypted') and self.encryption:
            try:
                message['content'] = self.encryption.decrypt(message['content'])
                message['encrypted'] = False
            except Exception:
                pass
        return message
    
    def mark_as_read(self, sender: str, receiver: str) -> int:
        """Mark all messages in a conversation as read."""
        conv_id = self._get_conversation_id(sender, receiver)
        count = 0
        for msg in self._conversations.get(conv_id, []):
            if msg['receiver'] == receiver and not msg['read']:
                msg['read'] = True
                count += 1
        return count
    
    def get_unread_count(self, username: str) -> int:
        """Get total unread messages for a user."""
        count = 0
        for messages in self._conversations.values():
            for msg in messages:
                if msg['receiver'] == username and not msg['read']:
                    count += 1
        return count
