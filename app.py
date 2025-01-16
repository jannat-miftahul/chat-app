from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from collections import deque, OrderedDict
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
message_queue = deque()  # For FCFS and FIFO
lru_message_queue = OrderedDict()  # For LRU
priority_queue = []  # For Priority Scheduling

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    username = users.get(request.sid, "Anonymous")
    timestamp = time.time()
    priority = 1  # Default priority, you can change this based on your criteria
    
    # Add message to FCFS/FIFO queue
    message_queue.append((username, msg))
    
    # Add message to LRU queue
    lru_message_queue[(username, msg)] = timestamp
    
    # Add message to Priority queue
    priority_queue.append((priority, username, msg))
    priority_queue.sort(reverse=True)  # Sort by priority (highest first)
    
    # Process messages based on the desired algorithm
    # process_fcfs_queue()
    # process_fifo_queue()
    # process_lru_queue()
    process_round_robin_queue()
    # process_priority_queue()

def process_fcfs_queue():
    while message_queue:
        username, msg = message_queue.popleft()
        print(f"Message from {username}: {msg}")
        send(f"{username}: {msg}", broadcast=True)

def process_fifo_queue():
    while message_queue:
        username, msg = message_queue.popleft()
        print(f"Message from {username}: {msg}")
        send(f"{username}: {msg}", broadcast=True)

def process_lru_queue():
    while lru_message_queue:
        lru_message = min(lru_message_queue, key=lru_message_queue.get)
        username, msg = lru_message
        del lru_message_queue[lru_message]
        print(f"Message from {username}: {msg}")
        send(f"{username}: {msg}", broadcast=True)

def process_round_robin_queue(time_slice=1):
    while message_queue:
        username, msg = message_queue.popleft()
        print(f"Message from {username}: {msg}")
        send(f"{username}: {msg}", broadcast=True)
        time.sleep(time_slice)  # Simulate time slice

def process_priority_queue():
    while priority_queue:
        priority, username, msg = priority_queue.pop(0)
        print(f"Message from {username} with priority {priority}: {msg}")
        send(f"{username}: {msg}", broadcast=True)

@socketio.on('connect')
def handle_connect():
    print("A user connected!")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users.pop(request.sid)
        print(f"User {username} disconnected!")
        send(f"{username} has left the chat", broadcast=True)
        emit('update_user_list', list(users.values()), broadcast=True)

@socketio.on('set_username')
def handle_set_username(username):
    users[request.sid] = username
    send(f"{username} has joined the chat", broadcast=True)
    emit('update_user_list', list(users.values()), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
