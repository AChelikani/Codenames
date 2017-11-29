from enum import Enum
from flask import Blueprint, render_template, session, url_for
from game_code import GameCode
from game_store import game_store
from keys import GAME_CODE_KEY, PLAYER_ID_KEY
from utils import get_session_data
from __main__ import socketio


game = Blueprint('game', __name__, template_folder='templates')

class GameEvent(Enum):
    TURN = 'game_turn'
    STOP = 'game_stop'
    PAUSE = 'game_pause'


# TODO this whole route
@game.route('/g/<game_code>')
def game_data(game_code):
    game_code_obj = GameCode(game_code)
    if not game_store.contains_game(game_code_obj):
        # TODO error handling
        pass
    player_id = session[PLAYER_ID_KEY]
    if not player_id:
        # TODO
        return 'TODO: You do not have a player id, probably cause you haven\'t lobbied up!'

    if game_store.is_player_dangling(game_code_obj, player_id):
        player = game_store.restore_player(game_code_obj, player_id)
    else:
        return 'TODO: you are not in this game!'

    return render_template(
       'game.html',
       game_bundle=game_store.get_game_bundle(game_code_obj),
       player_role=player.role.value
   )


@socketio.on('player turn')
def player_turn(message):
    try:
        game_code_raw, player_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return
    game_code = GameCode(game_code_raw)
    game_manager = game_store.get_game_bundle(game_code)
    player_id = session[PLAYER_ID_KEY]
    player = game_manager.get_player(player_id)

    if player.role == PlayerRole.SPYMASTER:
        # data = stringified {"Clue" : clueword, "Num" : #guesses}
        pass
    else:
        # data =
        pass


@socketio.on('pause game')
def player_pause_game(message):
	raise NotImplementedError("Please Implement this method")

@socketio.on('end game')
def player_end_game(message):
	raise NotImplementedError("Please Implement this method")
