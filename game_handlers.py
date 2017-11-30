from enum import Enum
from flask import Blueprint, render_template, session, url_for
from config import global_config as config
from game_code import GameCode
from game_store import game_store
from constants import GAME_CODE_KEY, CLIENT_ID_KEY
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
        return render_template('rejoin.html')
    game_manager = game_store.get_game(game_code_obj)

    if CLIENT_ID_KEY not in session:
        return render_template('rejoin.html')

    client_id = session[CLIENT_ID_KEY]

    if game_manager.has_active_client(client_id):
        client = game_manager.get_client(client_id)
    elif game_manager.has_dangling_client(client_id):
        client = game_manager.restore_client(client_id)
    else:
        # TODO: redirect to lobby if game hasn't started
        return render_template('rejoin.html')

    # TODO figure out which player's turn it is
    player = list(client.get_players().values())[0]
    return render_template(
       'game.html',
       game_bundle=game_store.get_full_game_bundle(game_code_obj, player.role),
       player_role=player.role.value,
       board_size=config.getNumCards(),
   )


@socketio.on(GameEvent.TURN.value)
def player_turn(message):
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    game_code = GameCode(game_code_raw)
    game_manager = game_store.get_game_bundle(game_code)
    game = game_manager.get_game()

    client_id = session[CLIENT_ID_KEY]
    client = game_manager.get_client(client_id)
    # TODO figure out which player's turn it is
    player = list(client.get_players().values())[0]

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
            pass
        elif (card_status == CardStatus.BOMB):
            # End game, bomb uncovered
            pass
        else:
            # Flip card, end turn
            pass


@socketio.on('pause game')
def player_pause_game():
    pass
	#raise NotImplementedError("Please Implement this method")

@socketio.on('end game')
def player_end_game(message):
	raise NotImplementedError("Please Implement this method")
