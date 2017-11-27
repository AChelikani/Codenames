from flask import Flask, render_template, request, abort, jsonify, send_from_directory
from config import global_config as config
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_manager import GameManager
from game_code import GameCode, generate_unique_game_code
from game_store import ActiveGameStore
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Active games store
game_store = ActiveGameStore()

# Home page for game creation and game joining
@app.route('/')
def home():
    # Get all active games only for debugging for now
    return render_template('home.html', active_games=list(game_store.get_all_active_games()))

@app.route('/how_to_play')
def how_to_play():
    return render_template('how_to_play.html')

@app.route('/create')
def create_game():
    # TODO: Note that going on the create page and refreshing results in many games being
    # added to the active games dict, which is not desired. Unclear on a resolution
    # for this issue yet.
    new_code = game_store.create_game()
    return render_template('create.html', game_code=new_code)

@app.route('/join')
def join_game():
    return render_template('join.html', error_text="")

# Unique route serving game data
@app.route('/g/<game_code>')
def game_data(game_code):
    game_code_obj = GameCode(game_code)
    if game_store.contains_game(game_code_obj):
        # Return json object of game state
        # TODO: 1) determine how we want to serialize game data
        #       2) share models between front and backends
        #       3) validate whether or not this user is a spymaster and should
        #          see the map
        #       4) if the game has not started, redirect to lobby
        return render_template(
            'game.html',
            game_bundle=game_store.get_game_bundle(game_code_obj)
        )
    else:
        # Temporarily create the game if it doesn't exist, just to speed up
        # dev
        game_store.create_game(game_code_obj)
        return game_data(game_code)

# Unique route for the game lobby before the game begins
@app.route('/l/<game_code>')
def game_lobby(game_code):
    game_code_obj = GameCode(game_code)
    if game_store.contains_game(game_code_obj):
        return render_template('lobby.html', game_code=game_code_obj.serialize())
    else:
        abort(404)

@app.route('/add_to_lobby/', methods=['POST'])
def add_to_lobby():
    game_code_str = request.form["game_code"]
    game_code = GameCode(game_code_str)
    if game_store.contains_game(game_code):
        return render_template('lobby.html', game_code=game_code.serialize())
    else:
        return render_template('join.html', error_text="Invalid game code")

# Socket listeners for lobby actions
# Handles the initial connection of a player to a lobby
@socketio.on('player connect')
def player_join_lobby(message):
    # TODO: sid should be replaced with some kind of cookie
    sid = request.sid
    game_code_raw = message['game_code']
    game_code = GameCode(game_code_raw)

    if not game_store.contains_game(game_code):
        # TODO error handling
        return

    game_manager = game_store.get_game(game_code)

    # Send the new player the current lobby state
    players = [p.serialize() for p in game_manager.get_players().values()]
    emit('update', {
        'players': players
    }, room=game_code)

    # Add the user to the game and to the socket room
    player = game_store.add_player(sid, game_code)
    join_room(game_code)

    # Notify all players in the lobby of the new user
    emit('player connect', {
        'player': player.serialize()
    }, broadcast=True, room=game_code)

@socketio.on('disconnect')
def player_leave_lobby():
    sid = request.sid

    if not game_store.contains_player(sid):
        return
        
    game_code = game_store.get_game_code(sid)

    if not game_store.contains_game(sid):
        return

    player = game_store.remove_player(sid, game_code)
    leave_room(game_code)
    emit('player disconnect', {
        'player': player.serialize()
    }, broadcast=True, room=game_code)

@socketio.on('player switch team')
def player_switch_team():
    sid = request.sid

    if not game_store.contains_player(sid):
        return

    game_code = game_store.get_game_code(sid)

    if not game_store.contains_game(game_code):
        return

    game_manager = game_store.get_game(game_code)

    game_manager.switch_player_team(sid)

    players = [p.serialize() for p in game_manager.get_players().values()]
    emit('update', {
        'players': players
    }, broadcast=True, room=game_code)

@socketio.on('player switch role')
def player_switch_role():
    sid = request.sid

    if not game_store.contains_player(sid):
        return

    game_code = game_store.get_game_code(sid)

    if not game_store.contains_game(game_code):
        return

    game_manager = game_store.get_game(game_code)

    game_manager.switch_player_role(sid)

    players = [p.serialize() for p in game_manager.get_players().values()]
    emit('update', {
        'players': players
    }, broadcast=True, room=game_code)


@socketio.on('start game')
def player_start_game(message):
	raise NotImplementedError("Please Implement this method")

# Socket listeners for game actions

@socketio.on('pause game')
def player_pause_game(message):
	raise NotImplementedError("Please Implement this method")

@socketio.on('end game')
def player_end_game(message):
	raise NotImplementedError("Please Implement this method")

@socketio.on('player turn')
def player_turn(message):
	raise NotImplementedError("Please Implement this method")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static','img','icons'),
                               'question_mark_icon.ico')

if __name__ == "__main__":
    socketio.run(app)
