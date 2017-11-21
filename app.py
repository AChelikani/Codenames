from flask import Flask
from codename_game import *

app = Flask(__name__)

active_games = {}

# Home page for game creation and game joining
@app.route('/')
def home():
    return '<p> Routes </p> <p> /active is all active games </p> <p> /some_game_name_here creates a game with that url </p>'

# Get all active games only for debugging
@app.route('/active')
def active():
    all_active_games = "\n".join(active_games.keys())
    return all_active_games

# Unique route for game page
@app.route('/<game_code>')
def game(game_code):
    # TODO: Add checking around max capacity of room, other things
    if game_code in active_games:
        # Return page showing current state of game
        print active_games[game_code]
        return game_code + ' game is already active'
    else:
        active_games[game_code] = CodenameGame()
        print active_games[game_code]
        return game_code + ' game created'


if __name__ == "__main__":
    app.run()
