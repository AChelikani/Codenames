from client_manager import ClientEvent
from constants import GAME_CODE_KEY, CLIENT_ID_KEY
from enum import Enum
from error_handling import ErrorHandler
from flask import Blueprint, render_template, abort, session, request, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from game_code import GameCode
from game_store import game_store
from utils import get_session_data
from __main__ import socketio


lobby = Blueprint('lobby', __name__, template_folder='templates')


@lobby.route('/l/<game_code>')
def game_lobby(game_code):
    game_code_obj = GameCode(game_code)
    session[GAME_CODE_KEY] = game_code

    if game_store.contains_game(game_code_obj):
        return render_template(
            'lobby.html',
            game_code=game_code_obj.serialize(),
            client_id_key=CLIENT_ID_KEY,
            ClientEvent=ClientEvent,
        )
    else:
        abort(404)

@lobby.route('/add_to_lobby/', methods=['POST'])
def add_to_lobby():
    game_code_str = request.form["game_code"]
    game_code = GameCode(game_code_str)
    if game_store.contains_game(game_code):
        return redirect(url_for('lobby.game_lobby', game_code=game_code.serialize()))
    else:
        return redirect(url_for('create.join_game', error_text="Invalid game code"))


###  Socket listeners ###

def client_event_handler(client_event, data=None, skip_client_id=False):
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(ClientEvent.UPDATE, game_code)
        return

    game_manager = game_store.get_game(game_code)

    try:
        client, events = game_manager.handle_client_event(client_id, client_event, data)
    except Exception as e:
        emit('error', str(e))

    for event in events:
        event.emit()
    return client

@socketio.on(ClientEvent.CONNECT.value)
def client_connect(cookie):
    if GAME_CODE_KEY not in session:
        # TODO: error handling
        return
    game_code_raw = session[GAME_CODE_KEY]
    game_code = GameCode(game_code_raw)

    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(ClientEvent.CONNECT, game_code)
        return

    game_manager = game_store.get_game(game_code)

    try:
        client, events = game_manager.handle_client_event(
            client_id=None,
            client_event=ClientEvent.CONNECT,
            data=cookie
        )
    except Exception as e:
        emit('error', str(e))

    for event in events: event.emit()

    # Store the client id and game code in the session for further requests
    session[CLIENT_ID_KEY] = client.id

    # Add the client's socket to the socket room
    join_room(game_code)

    # emit an update to the clients
    game_manager.get_lobby_update_event().emit()


@socketio.on(ClientEvent.ADD_PLAYER.value)
def add_player():
    client_event_handler(ClientEvent.ADD_PLAYER)

@socketio.on(ClientEvent.DELETE_PLAYER.value)
def delete_player(player_id):
    client_event_handler(ClientEvent.DELETE_PLAYER, player_id)

@socketio.on(ClientEvent.SWITCH_TEAM.value)
def player_switch_team(player_id):
    client_event_handler(ClientEvent.SWITCH_TEAM, player_id)

@socketio.on(ClientEvent.SWITCH_ROLE.value)
def player_switch_role(player_id):
    client_event_handler(ClientEvent.SWITCH_ROLE, player_id)

@socketio.on(ClientEvent.INIT_START_GAME.value)
def player_start_game():
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    game_code = GameCode(game_code_raw)
    emit(ClientEvent.START_GAME.value, url_for('game.game_data', game_code=game_code), room=game_code, broadcast=True)

# TODO: this is problematic.
# Socket.IO sends the same 'disconnect' event for all disconnects, so we cannot
# distinguish between a disconnect in a lobby or in a game.
# We could maybe use game state for this once that is implemented
@socketio.on('disconnect')
def client_leave_lobby():
    client_event_handler(ClientEvent.DISCONNECT)
