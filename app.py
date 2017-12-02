from flask import Flask, render_template, request, abort, send_from_directory, session, url_for, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
from config import global_config as config
from game_code import GameCode
from game_store import game_store
from utils import get_session_data
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a slightly better, not so predictable secret!'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
socketio = SocketIO(
    app,
    manage_session=False,
    logger=logging.getLogger('socketio'),
    engineio_logger=logging.getLogger('engineio')
)

from lobby_handlers import lobby
app.register_blueprint(lobby)

from game_handlers import game
app.register_blueprint(game)

from create_handlers import create
app.register_blueprint(create)


# TODO make this configurable via config
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.getLogger('socketio').setLevel(logging.WARNING)
logging.getLogger('engineio').setLevel(logging.WARNING)


# Home page for game creation and game joining
@app.route('/')
def home():
    # Get all active games only for debugging for now
    active_games = list(game_store.get_all_active_games())
    return render_template('home.html', active_games=active_games)

@app.route('/how_to_play')
def how_to_play():
    return render_template('how_to_play.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'img/icons/question_mark_icon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# TODO: add config for port,
if __name__ == "__main__":
    socketio.run(app)
