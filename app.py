from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    print(f"Message: {msg}")
    send(msg, broadcast=True)  # Broadcast the message to all users

@socketio.on('connect')
def handle_connect():
    print("A user connected!")

@socketio.on('disconnect')
def handle_disconnect():
    print("A user disconnected!")

if __name__ == '__main__':
    socketio.run(app, debug=True)
