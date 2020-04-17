from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from words import Words
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.redis = redis.Redis(host='localhost', port=6379, db=0)
app.words = Words(app.redis)
socketio = SocketIO(app, async_mode=None)
thread = None
thread_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('getNewLetterPair')
def get_new_letterpair():
    emit('letterpair', {'letterpair': app.words.random_pair("easy")})

@socketio.on("validWord")
def valid_word(message):
    emit("validWord", {"valid": app.words.valid_word(message['word'])})

# @socketio.on('my broadcast event')
# def message(message):
#     emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('keepalive')
def keepalive():
    emit('keepalive', {'keepalive': True})

@socketio.on('connect')
def connect():
    emit('my response', {'data': 'Connected'})
    print("Client connected")

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)