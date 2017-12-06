from card import CardStatus
from config import global_config as config
from constants import GAME_CODE_KEY, CLIENT_ID_KEY
from client_manager import ClientEvent
from error_handling import ErrorHandler
from flask import Blueprint, render_template, session, url_for
from flask_socketio import emit
from game import GameEvent
from game_code import GameCode
from game_store import game_store
from lobby_handlers import client_event_handler
from utils import get_session_data
from __main__ import socketio

game = Blueprint('game', __name__, template_folder='templates')


@game.route('/g/<game_code>')
def game_data(game_code):
    game_code_obj = GameCode(game_code)
    if not game_store.contains_game(game_code_obj):
        # TODO error handling
        return render_template('rejoin.html')
    session[GAME_CODE_KEY] = game_code
    game_manager = game_store.get_game(game_code_obj)

    if CLIENT_ID_KEY not in session:
        # Somehow the client lost their session between the lobby and the game
        # TODO: handle reconnection
        return render_template('rejoin.html')

    # TODO: This is emulating a lobby reconnection event using the session data
    #       I don't think this is a very good way to transition clients from
    #       the lobby to the game.
    #       Ideally, we don't even have a separate page, we serve the lobby
    #       and game on a single page.
    cookie = {}
    cookie[CLIENT_ID_KEY] = session[CLIENT_ID_KEY]
    try:
        client, events = game_manager.handle_client_event(
            client_id=None,
            client_event=ClientEvent.CONNECT,
            data=cookie
        )
        session[CLIENT_ID_KEY] = client.id
    except PermissionError as e:
        return render_template('rejoin.html')

    role_to_serve = client.has_spymaster()

    return render_template(
       'game.html',
       game_bundle=game_store.get_full_game_bundle(game_code_obj, role_to_serve),
       GameEvent=GameEvent,
       ClientEvent=ClientEvent,
   )


def game_event_handler(game_event, data=None):
    try:
        game_code_raw, client_id = get_session_data(session)
    except ValueError as err:
        emit('error', str(err))
        return

    game_code = GameCode(game_code_raw)
    if not game_store.contains_game(game_code):
        ErrorHandler.game_code_dne(GameEvent.UPDATE, game_code)
        return

    game_manager = game_store.get_game(game_code)

    #try:
    game, events = game_manager.handle_game_event(client_id, game_event, data)
    for event in events: event.emit()
    return game
    #except Exception as e:
    #
    #    emit('error', str(e))
    #    return None



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


@socketio.on(GameEvent.CHOOSE_WORD.value)
def choose_word(word):
    game_event_handler(GameEvent.CHOOSE_WORD, word)

@socketio.on(GameEvent.SUBMIT_CLUE.value)
def submit_clue(clue):
    game_event_handler(GameEvent.SUBMIT_CLUE, clue)

@socketio.on('pause game')
def player_pause_game():
	raise NotImplementedError("Please Implement this method")

@socketio.on('end game')
def player_end_game(message):
	raise NotImplementedError("Please Implement this method")
