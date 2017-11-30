from enum import Enum
from flask import Blueprint, render_template, session, url_for
from config import global_config as config
from game_code import GameCode
from game_store import game_store
from keys import GAME_CODE_KEY, PLAYER_ID_KEY
from utils import get_session_data
from __main__ import socketio
from codename_card import CardStatus

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
        return 'TODO: game store doesn\'t have game code (uh oh)'

    if PLAYER_ID_KEY not in session:
        return 'TODO: You do not have a player id, probably cause you haven\'t lobbied up!'

    player_id = session[PLAYER_ID_KEY]

    if game_store.does_player_exist(game_code_obj, player_id):
        game_manager = game_store.get_game(game_code_obj)
        player = game_manager.get_player(player_id)
    elif game_store.is_player_dangling(game_code_obj, player_id):
        player = game_store.restore_player(game_code_obj, player_id)
    else:
        return 'TODO: your player has been lost'

    print player.role.value
    return render_template(
       'game.html',
       game_bundle=game_store.get_full_game_bundle(game_code_obj, player.role),
       player_role=player.role.value,
       board_size=config.getNumCards(),
   )


@socketio.on(GameEvent.TURN.value)
def player_turn(message):
    try:
        game_code_raw, player_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    game_code = GameCode(game_code_raw)
    game_manager = game_store.get_game_bundle(game_code)
    game = game_manager.get_game()

    player_id = session[PLAYER_ID_KEY]
    player = game_manager.get_player(player_id)

    if player.role == PlayerRole.SPYMASTER:
        # data = {"Clue" : clueword, "Num" : #guesses}
        clue = message['Clue']
        num_guesses = message['Num']

        # TODO: Verification on clue and num_guesses

        # Construct clue object and add to game state
        game.set_current_clue(clue, num_guesses)

    else:
        # data = {"Word" : word}
        guessed_word = message['Word']
        card = game.get_card_by_word(guessed_word)
        current_turn = game.current_turn

        is_correct, card_status = game.make_guess(guessed_word)
        if (is_correct):
            # Proceed with turn
        elif (card_status == CardStatus.BOMB):
            # End game, bomb uncovered
        else:
            # Flip card, end turn


@socketio.on('pause game')
def player_pause_game():
    print "testing"
	#raise NotImplementedError("Please Implement this method")

@socketio.on('end game')
def player_end_game(message):
	raise NotImplementedError("Please Implement this method")
