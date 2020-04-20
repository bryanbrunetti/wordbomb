import config
import threading
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
stop_game = go_next = False
# TODO: look into using thread events instead of these flags

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
    global thread, stop_game
    if not thread:
        start_new_game()
    elif not len(game_state.current_players()):
        end_game()
        start_new_game()
    else:
        emit("error", {"message": "Game already running"})

def end_game():
    global thread, stop_game
    stop_game = True
    if thread:
        thread.join()
        thread = None
        stop_game = False

def start_new_game():
    socketio.emit("newGameStarted")
    next_player()
    thread = socketio.start_background_task(start_game_tick)

@app.route("/join", methods=["POST"])
def join():
    session["player"] = {"name": players.name(request.form["playerName"]), "id": players.get_next_id()}
    return redirect(url_for("game"))

@socketio.on("validWord")
@player_required
def valid_word(message):
    active_player = game_state.get_active_player()
    if active_player and int(active_player['id']) == int(session['player']['id']):
        global go_next
        is_valid = game_state.valid_word(message)
        go_next = True if is_valid else False
        emit("validWord", is_valid, broadcast=True)


@socketio.on("guessUpdate")
@player_required
def guess_update(message):
    active_player = game_state.get_active_player()
    if active_player and int(session['player']['id']) == int(active_player['id']):
        emit("guessUpdate", {"guess": message}, broadcast=True)


@socketio.on('keepalive')
@player_required
def keepalive():
    emit('keepalive', {'keepalive': players.keepalive(session['player']), "player": session["player"]["name"]}, room=request.sid)


@socketio.on('connect')
@player_required
def connect():
    players.add(session['player'])
    emit("playerid", session['player'], room=request.sid)
    emit("playerJoined", {"players": game_state.current_players()}, broadcast=True)


@socketio.on('disconnect')
@player_required
def disconnect():
    players.remove(session["player"])
    emit("playerLeft", {"players": game_state.current_players()}, broadcast=True)
    print(f"Client disconnected: {session}")

def start_game_state():
    global thread, stop_game
    while True:

        socketio.sleep(1)

def start_game_tick():
    time = app.round_time
    global stop_game, go_next
    while True:
        if not len(game_state.current_players()) or stop_game:
            return

        if go_next:
            time = 10
            next_player()
            go_next = False
            continue

        if time >= 0:
            socketio.emit('time', {'time': time}, broadcast=True)
            time -= 1
            socketio.sleep(1)
        else:
            socketio.emit("wrong", broadcast=True)
            next_player()
            time = 10


def next_player():
    next_player = game_state.next_player()
    game_state.set_active_player_id(next_player["id"])
    socketio.emit("nextPlayer", next_player, broadcast=True)
    socketio.emit("newLetterPair", {"letterpair": game_state.next_letterpair()})


if __name__ == '__main__':
    socketio.run(app)
