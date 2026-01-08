"""
Configuration settings for QuikTalk Chat Application
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'quiktalk-secret-key-2024')
    DEBUG = False
    
    # Server settings
    HOST = '127.0.0.1'
    PORT = 5000
    
    # SocketIO settings
    CORS_ALLOWED_ORIGINS = "*"
    
    # Encryption settings
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', None)
    
    # Logging settings
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    LOG_FILE = 'quiktalk.log'
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5
    
    # Chat settings
    MAX_MESSAGE_LENGTH = 1000
    MAX_ROOM_NAME_LENGTH = 50
    DEFAULT_ROOM = 'General'
    
    # Message history settings
    MESSAGE_HISTORY_LIMIT = 100


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])()
