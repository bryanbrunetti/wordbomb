import config
from threading import Lock
from flask import Flask, render_template, request, url_for, session, redirect
from flask_socketio import SocketIO, emit
from players import Players
from words import Words
from game_state import GameState
from authentication import player_required

app = Flask(__name__)
config.load(app)
words = Words(app)
players = Players(app)
game_state = GameState(app)
socketio = SocketIO(app, async_mode=None)

thread = None
stop_game = False

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game')
@player_required
def game():
    return render_template("game.html", player=session["player"])


@socketio.on("startGame")
@player_required
def start_game():
    global thread, end_game
    print("startGame called")
    if not thread:
        thread = socketio.start_background_task(start_game_tick)
    else:
        emit("error", {"message": "Game already running"})

@socketio.on("endGame")
def end_game():
    global thread, stop_game
    stop_game = True
    if thread:
        thread.join()
        thread = None
        stop_game = False


@app.route("/join", methods=["POST"])
def join():
    session["player"] = {"name": players.name(
        request.form["playerName"]), "id": players.get_next_id()}
    return redirect(url_for("game"))


@socketio.on('getNewLetterPair')
@player_required
def get_new_letterpair():
    print(f"Player: {session} requested a new letterpair")
    emit('letterpair', {'letterpair': words.random_pair("easy")})


@socketio.on("validWord")
@player_required
def valid_word(message):
    emit("validWord", {"valid": words.valid_word(message['word'])})


@socketio.on('keepalive')
@player_required
def keepalive():
    emit('keepalive', {'keepalive': players.keepalive(session['player'])})


@socketio.on('connect')
@player_required
def connect():
    players.add(session['player'])
    emit("players", {"players": game_state.current_players()})
    print(f"Client connected: {session}")


@socketio.on('disconnect')
@player_required
def disconnect():
    players.remove(session["player"])


def start_game_tick():
    time = app.round_time
    global stop_game
    while True:
        if not len(game_state.current_players()) or stop_game:
            return

        if time >= 0:
            socketio.emit('time', {'time': time}, broadcast=True)
            time -= 1
            socketio.sleep(1)
        else:
            next_player = game_state.next_player()
            game_state.set_active_player_id(next_player["id"])
            socketio.emit("next_player", {"player": next_player}, broadcast=True)
            time = 10


if __name__ == '__main__':
    socketio.run(app)
