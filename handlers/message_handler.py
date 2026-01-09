"""
Message Handler for processing chat messages
"""
from collections import deque, OrderedDict
from datetime import datetime
from typing import Tuple, Optional
import time


class MessageHandler:
    """
    Handles message processing with various scheduling algorithms.
    
    Features:
    - Multiple scheduling algorithms (FCFS, FIFO, LRU, Round Robin, Priority)
    - Message validation
    - Message formatting
    - Timestamp management
    """
    
    def __init__(self, max_message_length: int = 1000):
        """
        Initialize the message handler.
        
        Args:
            max_message_length: Maximum allowed message length
        """
        self.max_message_length = max_message_length
        
        # Message queues for different algorithms
        self.fcfs_queue = deque()
        self.fifo_queue = deque()
        self.lru_queue = OrderedDict()
        self.priority_queue = []
        self.round_robin_queue = deque()
        
        # Current algorithm
        self.current_algorithm = 'FCFS'
    
    def validate_message(self, message: str) -> Tuple[bool, str]:
        """
        Validate a message before processing.
        
        Args:
            message: The message to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message:
            return False, "Message cannot be empty"
        
        if len(message) > self.max_message_length:
            return False, f"Message exceeds maximum length of {self.max_message_length} characters"
        
        # Strip whitespace
        message = message.strip()
        
        if not message:
            return False, "Message cannot be empty"
        
        return True, ""
    
    def format_message(self, username: str, message: str, room: str = 'general',
                      message_type: str = 'text', encrypted: bool = False) -> dict:
        """
        Format a message for transmission.
        
        Args:
            username: Sender's username
            message: Message content
            room: Room ID
            message_type: Type of message
            encrypted: Whether the message is encrypted
            
        Returns:
            Formatted message dictionary
        """
        return {
            'id': f"{username}_{int(time.time() * 1000)}",
            'sender': username,
            'content': message,
            'room': room,
            'type': message_type,
            'encrypted': encrypted,
            'timestamp': datetime.now().isoformat(),
            'unix_timestamp': time.time()
        }
    
    def add_to_queue(self, username: str, message: str, priority: int = 1) -> None:
        """
        Add a message to all scheduling queues.
        
        Args:
            username: Sender's username
            message: Message content
            priority: Message priority (for priority scheduling)
        """
        timestamp = time.time()
        msg_data = (username, message, timestamp)
        
        # FCFS/FIFO queue
        self.fcfs_queue.append(msg_data)
        self.fifo_queue.append(msg_data)
        
        # LRU queue
        self.lru_queue[(username, message)] = timestamp
        
        # Priority queue
        self.priority_queue.append((priority, timestamp, username, message))
        self.priority_queue.sort(key=lambda x: (-x[0], x[1]))  # Higher priority first, then FIFO
        
        # Round Robin queue
        self.round_robin_queue.append(msg_data)
    
    def process_fcfs(self) -> Optional[Tuple[str, str]]:
        """
        Process message using First Come First Serve algorithm.
        
        Returns:
            Tuple of (username, message) or None
        """
        if self.fcfs_queue:
            username, message, _ = self.fcfs_queue.popleft()
            return username, message
        return None
    
    def process_fifo(self) -> Optional[Tuple[str, str]]:
        """
        Process message using FIFO algorithm.
        
        Returns:
            Tuple of (username, message) or None
        """
        if self.fifo_queue:
            username, message, _ = self.fifo_queue.popleft()
            return username, message
        return None
    
    def process_lru(self) -> Optional[Tuple[str, str]]:
        """
        Process message using Least Recently Used algorithm.
        
        Returns:
            Tuple of (username, message) or None
        """
        if self.lru_queue:
            # Get the least recently used (oldest timestamp)
            lru_key = min(self.lru_queue, key=self.lru_queue.get)
            del self.lru_queue[lru_key]
            return lru_key
        return None
    
    def process_round_robin(self, time_slice: float = 0.1) -> Optional[Tuple[str, str]]:
        """
        Process message using Round Robin algorithm.
        
        Args:
            time_slice: Time slice for each message (in seconds)
            
        Returns:
            Tuple of (username, message) or None
        """
        if self.round_robin_queue:
            username, message, _ = self.round_robin_queue.popleft()
            time.sleep(time_slice)  # Simulate time slice
            return username, message
        return None
    
    def process_priority(self) -> Optional[Tuple[str, str]]:
        """
        Process message using Priority Scheduling algorithm.
        
        Returns:
            Tuple of (username, message) or None
        """
        if self.priority_queue:
            priority, timestamp, username, message = self.priority_queue.pop(0)
            return username, message
        return None
    
    def process_message(self, algorithm: str = None) -> Optional[Tuple[str, str]]:
        """
        Process a message using the specified or current algorithm.
        
        Args:
            algorithm: Algorithm to use (FCFS, FIFO, LRU, ROUND_ROBIN, PRIORITY)
            
        Returns:
            Tuple of (username, message) or None
        """
        algo = algorithm or self.current_algorithm
        
        processors = {
            'FCFS': self.process_fcfs,
            'FIFO': self.process_fifo,
            'LRU': self.process_lru,
            'ROUND_ROBIN': self.process_round_robin,
            'PRIORITY': self.process_priority
        }
        
        processor = processors.get(algo.upper(), self.process_fcfs)
        return processor()
    
    def set_algorithm(self, algorithm: str) -> bool:
        """
        Set the current scheduling algorithm.
        
        Args:
            algorithm: Algorithm name
            
        Returns:
            True if successful
        """
        valid_algorithms = ['FCFS', 'FIFO', 'LRU', 'ROUND_ROBIN', 'PRIORITY']
        if algorithm.upper() in valid_algorithms:
            self.current_algorithm = algorithm.upper()
            return True
        return False
    
    def get_queue_sizes(self) -> dict:
        """Get the current size of all message queues."""
        return {
            'fcfs': len(self.fcfs_queue),
            'fifo': len(self.fifo_queue),
            'lru': len(self.lru_queue),
            'priority': len(self.priority_queue),
            'round_robin': len(self.round_robin_queue)
        }
    
    def clear_queues(self) -> None:
        """Clear all message queues."""
        self.fcfs_queue.clear()
        self.fifo_queue.clear()
        self.lru_queue.clear()
        self.priority_queue.clear()
        self.round_robin_queue.clear()
