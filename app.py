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
stop_game = go_next = False
# TODO: look into using thread events instead of these flags
# TODO: only allow current players to guess


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
        socketio.emit("newGameStarted")
        next_player()
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

@socketio.on("validWord")
@player_required
def valid_word(message):
    global go_next
    is_valid = game_state.valid_word(message)
    go_next = True if is_valid else False
    print(f"valid go next? {go_next}")
    emit("validWord", is_valid, broadcast=True)


@socketio.on("guessUpdate")
@player_required
def guess_update(message):
    emit("guessUpdate", {"guess": message}, broadcast=True)


@socketio.on('keepalive')
@player_required
def keepalive():
    emit('keepalive', {'keepalive': players.keepalive(
        session['player']), "player": session["player"]["name"]}, room=request.sid)


@socketio.on('connect')
@player_required
def connect():
    players.add(session['player'])
    emit("playerJoined", {
         "players": game_state.current_players()}, broadcast=True)
    print(f"Client connected: {session}")


@socketio.on('disconnect')
@player_required
def disconnect():
    players.remove(session["player"])
    emit("playerLeft", {
         "players": game_state.current_players()}, broadcast=True)
    print(f"Client disconnected: {session}")


def start_game_tick():
    time = app.round_time
    global stop_game, go_next
    while True:
        print(f"go_next?: {go_next}")
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
