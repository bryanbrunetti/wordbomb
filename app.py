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
    global thread
    socketio.emit("newGameStarted")
    game_state.start_new_game()
    next_player()
    thread = socketio.start_background_task(start_game_tick)
    

@app.route("/join", methods=["POST"])
def join():
    player_name = request.form["playerName"].replace(",","")
    player_name = player_name.replace(":","")
    session["player"] = {"name": players.name(player_name), "id": players.get_next_id()}
    return redirect(url_for("game"))

@socketio.on("validWord")
@player_required
def valid_word(message):
    active_player = game_state.get_active_player()
    if active_player and int(active_player['id']) == int(session['player']['id']):
        global go_next
        if game_state.valid_word(message):
            points = words.points_for(game_state.current_letterpair())
            score = game_state.player_add_points(active_player,points)
            emit("playerScore", {"player": active_player, "score": score}, broadcast=True)
            go_next = True
            emit("validWord", True, broadcast=True)
        else:
            emit("validWord", False, broadcast=True)


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
    emit("welcome", {
        "player": session['player'], 
        "gameState": current_game_state()
        }, room=request.sid)
    emit("playerJoined", session["player"], broadcast=True)

def current_game_state():
    # TODO: game state may have players waiting or current
    state = dict()
    state['currentPlayers'] = game_state.all_players()
    state['activePlayer'] = game_state.get_active_player()
    state['gameInProgress'] = is_game_in_progress()
    if state['gameInProgress']:
        state["letterPair"] = game_state.current_letterpair()
    return state

@socketio.on('disconnect')
@player_required
def disconnect():
    emit("playerLeft", session["player"], broadcast=True)

def is_game_in_progress():
    global thread, stop_game
    if thread:
        if thread.is_alive():
            return True
        else:
            end_game()
            return False
    else:
        return False

def start_game_tick():
    time = app.round_time
    global stop_game, go_next
    pubsub = app.redis.pubsub()
    pubsub.psubscribe("__keyevent@0__:expired")
    while True:
        msg = pubsub.get_message()
        if msg:
            if msg["type"] == "pmessage":
                if "player:" in msg["data"]:
                    game_state.remove_player_id(msg["data"].split(":")[1])
                elif "player_list" == msg["data"]:
                    return

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
            active_player = game_state.get_active_player()
            if active_player:
                player_state = game_state.get_player_state(active_player)
                if player_state:
                    lives = game_state.remove_life(active_player)
                    socketio.emit("playerLifeChange", {"player": active_player, "lives": lives}, broadcast=True)
                    if lives <= 0:
                        game_state.remove_player_id(active_player["id"])
                        socketio.emit("playerLost", active_player, broadcast=True)
            socketio.emit("wrong", broadcast=True)
            next_player()
            time = 10


def next_player():
    next_player = game_state.next_player()
    if next_player:
        game_state.set_active_player_id(next_player["id"])
        socketio.emit("nextPlayer", next_player, broadcast=True)
        socketio.emit("newLetterPair", {"letterpair": game_state.next_letterpair()})
    else:
        socketio.emit("gameOver")


if __name__ == '__main__':
    socketio.run(app)
