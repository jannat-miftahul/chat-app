"""
Logging Service for QuikTalk Chat Application
Provides comprehensive logging with file rotation and multiple log levels
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from functools import wraps
import traceback


class LoggerService:
    """
    Centralized logging service for the chat application.
    
    Features:
    - Console and file logging
    - Log rotation to prevent large files
    - Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Structured logging with timestamps
    - Performance logging decorator
    - Event-specific loggers
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: str = 'logs', log_file: str = 'quiktalk.log',
                 log_level: str = 'INFO', max_bytes: int = 10*1024*1024,
                 backup_count: int = 5):
        """
        Initialize the logging service.
        
        Args:
            log_dir: Directory to store log files
            log_file: Name of the main log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        if LoggerService._initialized:
            return
            
        self.log_dir = log_dir
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Setup loggers
        self._setup_main_logger()
        self._setup_event_loggers()
        
        LoggerService._initialized = True
    
    def _setup_main_logger(self):
        """Setup the main application logger."""
        self.logger = logging.getLogger('quiktalk')
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        file_path = os.path.join(self.log_dir, self.log_file)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_event_loggers(self):
        """Setup specialized loggers for different event types."""
        # Message logger
        self.message_logger = logging.getLogger('quiktalk.messages')
        msg_file = os.path.join(self.log_dir, 'messages.log')
        msg_handler = RotatingFileHandler(msg_file, maxBytes=self.max_bytes, backupCount=self.backup_count)
        msg_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.message_logger.addHandler(msg_handler)
        
        # Connection logger
        self.connection_logger = logging.getLogger('quiktalk.connections')
        conn_file = os.path.join(self.log_dir, 'connections.log')
        conn_handler = RotatingFileHandler(conn_file, maxBytes=self.max_bytes, backupCount=self.backup_count)
        conn_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.connection_logger.addHandler(conn_handler)
        
        # Room logger
        self.room_logger = logging.getLogger('quiktalk.rooms')
        room_file = os.path.join(self.log_dir, 'rooms.log')
        room_handler = RotatingFileHandler(room_file, maxBytes=self.max_bytes, backupCount=self.backup_count)
        room_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.room_logger.addHandler(room_handler)
        
        # Error logger
        self.error_logger = logging.getLogger('quiktalk.errors')
        error_file = os.path.join(self.log_dir, 'errors.log')
        error_handler = RotatingFileHandler(error_file, maxBytes=self.max_bytes, backupCount=self.backup_count)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d]\n%(message)s\n'
        ))
        self.error_logger.addHandler(error_handler)
    
    # Main logging methods
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log an error message with optional exception info."""
        self.logger.error(message, exc_info=exc_info)
        if exc_info:
            self.error_logger.error(f"{message}\n{traceback.format_exc()}")
    
    def critical(self, message: str, exc_info: bool = True):
        """Log a critical message with exception info."""
        self.logger.critical(message, exc_info=exc_info)
        self.error_logger.critical(f"{message}\n{traceback.format_exc()}")
    
    