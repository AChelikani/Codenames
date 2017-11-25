from flask import Flask, render_template
from flask import abort, jsonify
from codename_game import *
from flask_socketio import SocketIO, emit
from game_code import generate_unique_game_code

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

active_games = {}

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
        active_games[game_code] = CodenameGame()
        print(active_games[game_code])
        return game_code + ' game created'


@app.route('/create')
def create_game():
    code_len = config.getGameCodeLen()
    existing_codes = active_games.keys()
    new_code = generate_unique_game_code(code_len, existing_codes)
    active_games[new_code] = CodenameGame()
    return render_template('create.html', game_code=new_code)

@app.route('/join')
def join_game():
    return render_template('join.html')

# Unique route serving game data
@app.route('/g/<game_code>')
def game_data(game_code):
    if game_code in active_games:
        game = active_games[game_code]
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
            my_list=[1,2,3],
            starting_color=game.map_card.starting_color.name,
        )
    else:
        # Temporarily create the game if it doesn't exist, just to speed up
        # dev
        active_games[game_code] = CodenameGame()
        return game_data(game_code)

# Unique route for the game lobby before the game begins
@app.route('/l/<game_code>')
def game_lobby(game_code):
    return render_template('lobby.html');

# TODO: A test socket.io event
@socketio.on('test event')
def test_message(message):
    emit('test response', { 'data': 'rec\'d' })

if __name__ == "__main__":
    socketio.run(app)
