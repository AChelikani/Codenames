from client_manager import ClientManager, ClientEvent
from game import CodenameGame
from enum import Enum
from transitions import Machine
from utils import JSONUtils, EmitEvent


class GameState(Enum):
    IN_LOBBY = 0
    IN_GAME  = 1
    IN_ENDSCREEN = 2

class GameManager(object):
    states = [ GameState.IN_LOBBY, GameState.IN_GAME, GameState.IN_ENDSCREEN ]

    transitions = [
        ['start_game', GameState.IN_LOBBY, GameState.IN_GAME],
        ['pause_game', GameState.IN_GAME, GameState.IN_LOBBY],
        ['game_over', GameState.IN_GAME, GameState.IN_ENDSCREEN],
    ]

    def __init__(self, game_code):
        # Game code of game being managed.
        self.game_code = game_code
        # Generated codename game.
        self.game = CodenameGame()
        # Manager for clients (and players)
        self.client_manager = ClientManager()
        # Manager for displaying the right data to a client
        # self.display_manager = DisplayManager()
        self.machine = Machine(
            model=self,
            states=GameManager.states,
            initial=GameState.IN_LOBBY,
            transitions=GameManager.transitions,
        )

    def get_lobby_update_event(self):
        ''' Constructs a client UPDATE event based upon the current state. '''
        lobby_bundle = self.client_manager.get_lobby_bundle()
        return EmitEvent(
            ClientEvent.UPDATE.value,
            lobby_bundle,
            room=self.game_code,
            broadcast=True
        )

    def handle_client_event(self, client_id, client_event, data):
        ''' Passes client events down to the client manager to deal with and
            appends an UPDATE event.
        '''
        client_manager = self.client_manager
        client, events = client_manager.handle_event(client_id, client_event, data)
        events.append(self.get_lobby_update_event())
        return client, events

    def get_game(self):
        ''' Returns contained CodenamesGame object. '''
        return self.game

    def serialize_game(self):
        ''' Serializes contained game to JSON object along with game code. '''
        game_bundle = self.game.serialize()
        game_bundle['gameCode'] = str(self.game_code)
        return game_bundle

    def serialize_players(self):
        ''' Serializes players to JSON object. '''
        return self.client_manager.serialize_players()

    def serialize_players_mapping(self):
        ''' Serializes playerid to player mapping to JSON object. '''
        return self.client_manager.serialize_players_mapping()
