"""
QuikTalk - Real-Time Chat Application
Main application file with enhanced features
"""
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import time

# Import services
from services.encryption import EncryptionService
from services.logger import LoggerService
from services.rooms import RoomService

# Import handlers
from handlers.message_handler import MessageHandler
from handlers.room_handler import RoomHandler
from handlers.user_handler import UserHandler
from handlers.private_message_handler import PrivateMessageHandler

# Import configuration
from config import get_config

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins=config.CORS_ALLOWED_ORIGINS)

# Initialize services
logger = LoggerService(
    log_dir=config.LOG_DIR,
    log_file=config.LOG_FILE,
    log_level=config.LOG_LEVEL
)
encryption = EncryptionService(master_key=config.SECRET_KEY)
room_service = RoomService(default_room=config.DEFAULT_ROOM)

# Initialize handlers
message_handler = MessageHandler(max_message_length=config.MAX_MESSAGE_LENGTH)
user_handler = UserHandler(logger=logger)
room_handler = RoomHandler(room_service=room_service, logger=logger)
pm_handler = PrivateMessageHandler(encryption_service=encryption, logger=logger)

logger.info("QuikTalk application initialized successfully")


# ============ ROUTES ============
@app.route('/')
def home():
    return render_template('index.html')


# ============ CONNECTION EVENTS ============
@socketio.on('connect')
def handle_connect():
    logger.info(f"New connection: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    user = user_handler.unregister_user(request.sid)
    if user:
        # Leave all rooms
        left_rooms = room_handler.handle_disconnect(request.sid, user.display_name)
        
        # Notify others
        send(f"System: {user.display_name} has left the chat", broadcast=True)
        emit('update_user_list', user_handler.get_user_list(), broadcast=True)
        
        # Notify room members
        for room_id in left_rooms:
            emit('user_left_room', {
                'username': user.display_name,
                'room': room_id
            }, room=room_id)


@socketio.on('set_username')
def handle_set_username(username):
    user = user_handler.register_user(request.sid, username)
    
    # Auto-join general room
    room_handler.join_room('general', request.sid, user.display_name)
    join_room('general')
    
    send(f"System: {user.display_name} has joined the chat", broadcast=True)
    emit('update_user_list', user_handler.get_user_list(), broadcast=True)
    emit('username_set', {'username': user.display_name})
    
    # Send room list
    rooms = room_handler.get_rooms()
    emit('room_list', rooms)


# ============ MESSAGE EVENTS ============
@socketio.on('message')
def handle_message(data):
    username = user_handler.get_username(request.sid)
    if not username:
        return
    
    # Handle both string and dict messages
    if isinstance(data, str):
        msg = data
        room = 'general'
        encrypt = False
    else:
        msg = data.get('message', '')
        room = data.get('room', 'general')
        encrypt = data.get('encrypt', False)
    
    # Validate message
    is_valid, error = message_handler.validate_message(msg)
    if not is_valid:
        emit('error', {'message': error})
        return
    
    # Encrypt if requested
    if encrypt:
        try:
            msg = encryption.encrypt_for_room(room, msg)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
    
    # Format and store message
    formatted = message_handler.format_message(username, msg, room, encrypted=encrypt)
    room_service.add_message_to_history(room, formatted)
    
    # Log the message
    logger.log_message(username, 'broadcast', room)
    
    # Broadcast to room
    emit('receive_message', formatted, room=room)


# ============ ROOM EVENTS ============
@socketio.on('create_room')
def handle_create_room(data):
    username = user_handler.get_username(request.sid)
    if not username:
        return
    
    result = room_handler.create_room(data, username)
    emit('room_created', result)
    
    if result['success']:
        emit('room_list', room_handler.get_rooms(), broadcast=True)


@socketio.on('join_room')
def handle_join_room(data):
    username = user_handler.get_username(request.sid)
    if not username:
        return
    
    room_id = data.get('room_id', 'general')
    result = room_handler.join_room(room_id, request.sid, username)
    
    if result['success']:
        join_room(room_id)
        emit('joined_room', result)
        emit('user_joined_room', {
            'username': username,
            'room': room_id
        }, room=room_id)


@socketio.on('leave_room')
def handle_leave_room(data):
    username = user_handler.get_username(request.sid)
    if not username:
        return
    
    room_id = data.get('room_id')
    if room_id == 'general':
        emit('error', {'message': 'Cannot leave the general room'})
        return
    
    result = room_handler.leave_room(room_id, request.sid, username)
    
    if result['success']:
        leave_room(room_id)
        emit('left_room', result)
        emit('user_left_room', {
            'username': username,
            'room': room_id
        }, room=room_id)


@socketio.on('get_rooms')
def handle_get_rooms():
    result = room_handler.get_rooms()
    emit('room_list', result)


@socketio.on('get_room_members')
def handle_get_room_members(data):
    room_id = data.get('room_id', 'general')
    result = room_handler.get_room_members(room_id)
    emit('room_members', result)


# ============ PRIVATE MESSAGE EVENTS ============
@socketio.on('private_message')
def handle_private_message(data):
    sender = user_handler.get_username(request.sid)
    if not sender:
        return
    
    receiver = data.get('receiver')
    content = data.get('message', '')
    encrypt = data.get('encrypt', True)
    
    # Get receiver's socket ID
    receiver_sid = user_handler.get_socket_id_by_username(receiver)
    if not receiver_sid:
        emit('error', {'message': f'User {receiver} not found'})
        return
    
    # Send message
    message = pm_handler.send_message(sender, receiver, content, encrypt)
    
    # Send to receiver
    emit('private_message', message, room=receiver_sid)
    # Confirm to sender
    emit('private_message_sent', message)


@socketio.on('get_conversation')
def handle_get_conversation(data):
    username = user_handler.get_username(request.sid)
    if not username:
        return
    
    other_user = data.get('with_user')
    messages = pm_handler.get_conversation(username, other_user)
    
    # Decrypt messages
    decrypted = [pm_handler.decrypt_message(m.copy()) for m in messages]
    
    emit('conversation_history', {
        'with_user': other_user,
        'messages': decrypted
    })


# ============ UTILITY EVENTS ============
@socketio.on('get_stats')
def handle_get_stats():
    stats = {
        'users_online': user_handler.user_count(),
        'rooms': room_service.room_count(),
        'log_stats': logger.get_log_stats()
    }
    emit('stats', stats)


# ============ RUN APPLICATION ============
if __name__ == '__main__':
    logger.info(f"Starting QuikTalk on {config.HOST}:{config.PORT}")
    socketio.run(app, debug=config.DEBUG, host=config.HOST, port=config.PORT)
