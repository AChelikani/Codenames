from enum import Enum
from flask import Blueprint, render_template, abort, session, request, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from game_code import GameCode, generate_unique_game_code
from game_store import game_store
from error_handling import ErrorHandler
from utils import get_session_data
from keys import GAME_CODE_KEY, PLAYER_ID_KEY, OLD_ID_KEY
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


@lobby.route('/l/<game_code>')
def game_lobby(game_code):
    game_code_obj = GameCode(game_code)
    session[GAME_CODE_KEY] = game_code

    if game_store.contains_game(game_code_obj):
        return render_template(
            'lobby.html',
            game_code=game_code_obj.serialize(),
            old_id_key=OLD_ID_KEY,
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
def player_join_lobby(data):
    if GAME_CODE_KEY not in session:
        # TODO: error handling
        return
    game_code_raw = session[GAME_CODE_KEY]
    game_code = GameCode(game_code_raw)

    if not game_store.contains_game(game_code):
        # TODO error handling
        return

    existing_id = None
    if (OLD_ID_KEY in data and
        game_store.is_player_dangling(game_code, data[OLD_ID_KEY])):
        existing_id = data[OLD_ID_KEY]
        player = game_store.restore_player(game_code, existing_id)
    else:
        player = game_store.add_player(game_code)

    # Store the player id and game code in the session for further requests
    session[PLAYER_ID_KEY] = player.id

    # Add the player to the socket room
    join_room(game_code)

    emit(LobbyEvent.SET_ID.value, player.id)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)


@socketio.on(LobbyEvent.SWITCH_TEAM.value)
def player_switch_team():
    try:
        game_code_raw, player_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(LobbyEvent.SWITCH_TEAM, game_code)
        return

    game_manager = game_store.get_game(game_code)
    game_manager.switch_player_team(player_id)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)


@socketio.on(LobbyEvent.SWITCH_ROLE.value)
def player_switch_role():
    try:
        game_code_raw, player_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        # TODO: error handling
        return

    game_manager = game_store.get_game(game_code)
    game_manager.switch_player_role(player_id)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)


@socketio.on(LobbyEvent.INIT_START_GAME.value)
def player_start_game():
    try:
        game_code_raw, player_id = get_session_data(session)
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
def player_leave_lobby():
    game_code_raw, player_id = get_session_data(session)
    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        # TODO: error handling
        return

    player = game_store.remove_player(player_id, game_code)
    leave_room(game_code)
    lobby_bundle = game_store.get_lobby_bundle(game_code)
    emit(LobbyEvent.UPDATE.value, lobby_bundle, room=game_code, broadcast=True)
