from flask import Flask, render_template, request, abort, jsonify
from config import global_config as config
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_manager import GameManager
from game_code import generate_unique_game_code

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

active_games = {}

# Store mapping player ids to game ids
players_games = {}

# Home page for game creation and game joining
@app.route('/')
def home():
    # Get all active games only for debugging for now
    return render_template('home.html', active_games=list(active_games.keys()))

# Unique route for game page
@app.route('/<game_code>')
def game(game_code):
    # TODO: Add checking around max capacity of room, other things
    if game_code in active_games:
        # Return page showing current state of game
        print(active_games[game_code])
        return game_code + ' game is already active'
    else:
        active_games[game_code] = GameManager(game_code)
        print(active_games[game_code])
        return game_code + ' game created'

@app.route('/create')
def create_game():
    code_len = config.getGameCodeLen()
    existing_codes = active_games.keys()
    new_code = generate_unique_game_code(code_len, existing_codes)
    active_games[new_code] = GameManager(new_code)
    return render_template('create.html', game_code=new_code)

@app.route('/join')
def join_game():
    return render_template('join.html')

# Unique route serving game data
@app.route('/g/<game_code>')
def game_data(game_code):
    if game_code in active_games:
        game = active_games[game_code].game
        # Return json object of game state
        # TODO: 1) determine how we want to serialize game data
        #       2) share models between front and backends
        #       3) validate whether or not this user is a spymaster and should
        #          see the map
        #       4) if the game has not started, redirect to lobby
        # This is temporary to get things started.
        return render_template(
            'game.html',
            game_code=game_code,
            board_size=config.getNumCards(),
            map=[str(position.name) for position in game.map_card.map],
            words=[card.word for card in game.deck],
            starting_color=game.map_card.starting_color.name,
        )
    else:
        # Temporarily create the game if it doesn't exist, just to speed up
        # dev
        active_games[game_code] = GameManager(game_code)
        return game_data(game_code)

# Unique route for the game lobby before the game begins
@app.route('/l/<game_code>')
def game_lobby(game_code):
    if game_code in active_games:
        return render_template('lobby.html', game_code=game_code)
    else:
        abort(404)



# Socket listeners for lobby actions


# Handles the initial connection of a player to a lobby
@socketio.on('player connect')
def player_join_lobby(message):
    # TODO: sid should be replaced with some kind of cookie
    sid = request.sid
    game_code = message['game_code']

    if game_code not in active_games:
        # TODO error handling
        return

    game_manager = active_games[game_code]

    # Send the new player the current lobby state
    players = [p.serialize() for p in game_manager.get_players().values()]
    emit('update', {
        'players': players
    })

    # Add the user to the game and to the socket room
    player = game_manager.add_player(sid)
    players_games[sid] = game_code
    join_room(game_code)

    # Notify all players in the lobby of the new user
    emit('player connect', {
        'player': player.serialize()
    }, broadcast=True, room=game_code)

@socketio.on('disconnect')
def player_leave_lobby():
    sid = request.sid
    game_code = players_games.pop(sid, None)

    if game_code is None:
        return

    game_manager = active_games[game_code]
    player = game_manager.remove_player(sid)
    leave_room(game_code)
    emit('player disconnect', {
        'player': player.serialize()
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


if __name__ == "__main__":
    socketio.run(app)
