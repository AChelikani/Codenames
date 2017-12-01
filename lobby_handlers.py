from enum import Enum
from flask import Blueprint, render_template, abort, session, request, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from game_code import GameCode, generate_unique_game_code
from game_store import game_store
from error_handling import ErrorHandler
from utils import get_session_data
from constants import GAME_CODE_KEY, CLIENT_ID_KEY, OLD_ID_KEY
from __main__ import socketio


lobby = Blueprint('lobby', __name__, template_folder='templates')

class LobbyEvent(Enum):
    CONNECT = 'lobby_connect'
    SET_ID = 'lobby_set_id'
    UPDATE = 'lobby_update'
    SWITCH_ROLE = 'lobby_switch_role'
    SWITCH_TEAM = 'lobby_switch_team'
    INIT_START_GAME = 'lobby_init_start_game'
    START_GAME = 'lobby_start_game'
    ADD_PLAYER = 'add_player'
    DELETE_PLAYER = 'delete_player'
    RECEIVE_PLAYERS = 'receive_players'


@lobby.route('/l/<game_code>')
def game_lobby(game_code):
    game_code_obj = GameCode(game_code)
    session[GAME_CODE_KEY] = game_code

    if game_store.contains_game(game_code_obj):
        return render_template(
            'lobby.html',
            game_code=game_code_obj.serialize(),
            client_id_key=CLIENT_ID_KEY,
            LobbyEvent=LobbyEvent,
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

@socketio.on(LobbyEvent.CONNECT.value)
def client_join_lobby(cookie):
    if GAME_CODE_KEY not in session:
        # TODO: error handling
        return
    game_code_raw = session[GAME_CODE_KEY]
    game_code = GameCode(game_code_raw)

    if not game_store.contains_game(game_code):
        # TODO error handling
        emit('error', 'Game does not exist for game code')
        return

    game_manager = game_store.get_game(game_code)

    existing_id = None
    if (cookie and CLIENT_ID_KEY in cookie and
        game_manager.has_client(cookie[CLIENT_ID_KEY])):
        existing_id = cookie[CLIENT_ID_KEY]
        client = game_manager.restore_client(existing_id)
    else:
        client = game_store.add_new_client(game_code)

    # Store the client id and game code in the session for further requests
    session[CLIENT_ID_KEY] = client.id

    # Add the client to the socket room
    join_room(game_code)

    cookie = game_manager.get_client_cookie(client.id)
    emit(LobbyEvent.SET_ID.value, cookie)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)

@socketio.on(LobbyEvent.ADD_PLAYER.value)
def add_player():
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(LobbyEvent.SWITCH_TEAM, game_code)
        return
    game_manager = game_store.get_game(game_code)
    player = game_manager.add_new_player(client_id)
    cookie = game_manager.get_client_cookie(client_id)
    emit(LobbyEvent.RECEIVE_PLAYERS.value, cookie)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)

@socketio.on(LobbyEvent.DELETE_PLAYER.value)
def delete_player(player_id):
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(LobbyEvent.SWITCH_TEAM, game_code)
        return
    game_manager = game_store.get_game(game_code)
    if not game_manager.client_has_player(client_id, player_id):
        emit('error', 'You cannot change that player')
        return
    game_manager.delete_player(client_id, player_id)
    cookie = game_manager.get_client_cookie(client_id)
    emit(LobbyEvent.RECEIVE_PLAYERS.value, cookie)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)

@socketio.on(LobbyEvent.SWITCH_TEAM.value)
def player_switch_team(player_id):
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(LobbyEvent.SWITCH_TEAM, game_code)
        return
    game_manager = game_store.get_game(game_code)
    if not game_manager.client_has_player(client_id, player_id):
        # TODO: permissions error
        emit('error', 'TODO: permissions error')
        return
    game_manager.switch_player_team(client_id, player_id)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)


@socketio.on(LobbyEvent.SWITCH_ROLE.value)
def player_switch_role(player_id):
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        # TODO: error handling
        return

    game_manager = game_store.get_game(game_code)
    game_manager.switch_player_role(client_id, player_id)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)


@socketio.on(LobbyEvent.INIT_START_GAME.value)
def player_start_game():
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    # TODO: Add validation for number of different roles/num players on each team, etc.

    game_code = GameCode(game_code_raw)
    emit(LobbyEvent.START_GAME.value, url_for('game.game_data', game_code=game_code), room=game_code, broadcast=True)


# TODO: this is problematic.
# Socket.IO sends the same 'disconnect' event for all disconnects, so we cannot
# distinguish between a disconnect in a lobby or in a game.
# We could maybe use game state for this once that is implemented
@socketio.on('disconnect')
def client_leave_lobby():
    game_code_raw, client_id = get_session_data(session)
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        # TODO: error handling
        return

    client = game_store.remove_client(client_id, game_code)
    leave_room(game_code)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)
