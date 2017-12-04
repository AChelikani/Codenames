from constants import CLIENT_ID_KEY
from client import Client
from enum import Enum
from utils import JSONUtils, EmitEvent
from player import Player, PlayerTeam, PlayerRole


class PlayerConfigError(Enum):
    NONE = ''
    NO_RED_TEAM = 'Add a red team to get started.'
    NO_RED_SPYMASTER = 'Red team is missing a spymaster.'
    NO_RED_OPERATIVE = 'Red team is missing an operative.'
    NO_BLUE_TEAM = 'Add a blue team to get started.'
    NO_BLUE_SPYMASTER = 'Blue team is missing a spymaster.'
    NO_BLUE_OPERATIVE = 'Blue team is missing an operative.'


class ClientEvent(Enum):
    CONNECT = 'client_connect'
    SET_ID = 'client_set_id'
    UPDATE = 'client_update'
    SWITCH_ROLE = 'client_switch_role'
    SWITCH_TEAM = 'client_switch_team'
    INIT_START_GAME = 'client_init_start_game'
    START_GAME = 'client_start_game'
    ADD_PLAYER = 'client_add_player'
    DELETE_PLAYER = 'client_delete_player'
    RECEIVE_PLAYERS = 'client_receive_players'
    DISCONNECT = 'disconnect'


# Manages the clients (and therefore players) of a game
class ClientManager(object):
    states = [
        'valid', 'invalid'
    ]

    operative_errors = [PlayerConfigError.NO_RED_OPERATIVE, PlayerConfigError.NO_BLUE_OPERATIVE]

    red_team_errors = [
        PlayerConfigError.NO_RED_TEAM,
        PlayerConfigError.NO_RED_SPYMASTER,
        PlayerConfigError.NO_RED_OPERATIVE
    ]

    blue_team_errors = [
        PlayerConfigError.NO_BLUE_TEAM,
        PlayerConfigError.NO_BLUE_SPYMASTER,
        PlayerConfigError.NO_BLUE_OPERATIVE
    ]

    def __init__(self):
        # Player client mapping (maybe not necessary)
        self.player_clients = {}
        # Active clients of game.
        self.clients = {}
        # Disconnected clients of game (for in case they come back).
        self.dangling_clients = {}
        # Avatars being used for clients.
        self.used_avatars = []
        # Allow new players to join or not
        self.locked = False

    def handle_event(self, game_code, client_id, client_event, data):
        ''' Handles all client events given a client id, the event and data
            associated with the event.
         '''
        events = []
        client = None
        if client_event is ClientEvent.CONNECT:
            if (data and CLIENT_ID_KEY in data and \
                self.has_client(data[CLIENT_ID_KEY])):
                existing_id = data[CLIENT_ID_KEY]
                client = self.restore_client(existing_id)
            elif not self.locked:
                client = self.add_new_client()
            else:
                raise PermissionError("""Lobby is locked, no new players are
                                         permitted to join.""")
            cookie = client.get_cookie()
            events.append(EmitEvent(ClientEvent.SET_ID.value, cookie))
        elif client_event is ClientEvent.ADD_PLAYER:
            self.add_new_player(client_id)
        elif client_event is ClientEvent.DELETE_PLAYER:
            player_id = data
            if not self.client_has_player(client_id, player_id):
                raise PermissionError("""Client %s does not have permissions to
                                         delete player %s"""
                                         % (client_id, player_id))
            self.delete_player(client_id, player_id)
        elif client_event is ClientEvent.SWITCH_TEAM:
            player_id = data
            if not self.client_has_player(client_id, player_id):
                raise PermissionError("""Client %s does not have permissions to
                                         change player %s"""
                                         % (client_id, player_id))
            self.switch_player_team(client_id, player_id)
        elif client_event is ClientEvent.SWITCH_ROLE:
            player_id = data
            if not self.client_has_player(client_id, player_id):
                raise PermissionError("""Client %s does not have permissions to
                                         change player %s"""
                                         % (client_id, player_id))
            self.switch_player_role(client_id, player_id)
        elif client_event is ClientEvent.INIT_START_GAME:
            self.locked = True
            redirect_url = data
            events.append(EmitEvent(ClientEvent.START_GAME.value, redirect_url, room=game_code, broadcast=True))
        elif client_event is ClientEvent.DISCONNECT:
            self.remove_client(client_id)

        # If the event affects the state of the client cookie then emit an event
        # to update the client cookie.
        if client_event is ClientEvent.ADD_PLAYER or \
           client_event is ClientEvent.DELETE_PLAYER:
            client = self.get_client(client_id)
            cookie = client.get_cookie()
            events.append(EmitEvent(ClientEvent.RECEIVE_PLAYERS.value, cookie))

        return client, events

    def get_client(self, client_id):
        ''' Returns an active client if it exists. '''
        if client_id not in self.clients:
            ValueError('Client does not exist for id %s' % client_id)
        return self.clients[client_id]

    def get_num_clients(self):
        ''' Returns number of active clients. '''
        return len(self.clients)

    def add_client(self, client):
        ''' Adds new client to a client and tracks avatar. '''
        self.clients[client.id] = client
        players = client.get_players().values()
        for player in players:
            self.used_avatars.append(player.avatar)
        return client

    def add_new_player(self, client_id):
        ''' Add a player that fixes the player config error if one exists,
            otherwise add a random player.
        '''
        client = self.get_client(client_id)
        error = PlayerConfigError(self.get_player_config_error())
        new_role = PlayerRole.OPERATIVE if error in self.operative_errors else PlayerRole.SPYMASTER

        if error in self.red_team_errors:
            new_player = client.add_new_player(self.used_avatars, PlayerTeam.RED, new_role)
        elif error in self.blue_team_errors:
            new_player = client.add_new_player(self.used_avatars, PlayerTeam.BLUE, new_role)
        else:
            new_player = client.add_new_player(self.used_avatars)

        self.used_avatars.append(new_player.avatar)
        return new_player

    def add_new_client(self):
        ''' Creates new client and adds it. '''
        new_client = Client.new_client()
        self.add_client(new_client)
        return new_client

    def remove_client(self, client_id):
        ''' Removes client from active clients. '''
        client = self.clients.pop(client_id, None)
        players = client.get_players().values()
        for player in players:
            self.used_avatars.remove(player.avatar)
        self.dangling_clients[client_id] = client
        return client

    def get_clients(self):
        ''' Returns active client id to client mapping. '''
        return self.clients

    def has_active_client(self, client_id):
        ''' Returns whether the corresponding active client exists or not. '''
        return client_id in self.clients

    def has_dangling_client(self, client_id):
        ''' Returns whether the corresponding dangling client exists or not. '''
        return client_id in self.dangling_clients

    def get_active_client(self, client_id):
        ''' Returns corresponding active client if exists else None. '''
        if client_id in self.clients:
            return self.clients[client_id]
        return None

    def get_dangling_client(self, client_id):
        ''' Returns corresponding dangling client if exists else None. '''
        if client_id in self.dangling_clients:
            return self.dangling_clients[client_id]
        return None

    def has_client(self, client_id):
        ''' Returns True if client_id is in clients or dangling_clients. '''
        return client_id in self.clients or client_id in self.dangling_clients

    def get_dangling_clients(self):
        ''' Returns disconnectd client id to client mapping. '''
        return self.dangling_clients

    def restore_client(self, client_id):
        ''' Restores disconnected client to active client mapping. '''
        if client_id in self.clients:
            return self.get_active_client(client_id)
        client = self.dangling_clients.pop(client_id)
        players = client.get_players().values()
        for player in players:
            avatar = Player._get_avatar(self.used_avatars, pref=player.avatar)
            player = Player(player.id, player.team, player.role, avatar)
            self.used_avatars.append(player.avatar)
        return self.add_client(client)

    def get_players(self):
        players = {}
        for client in self.clients.values():
            client_players = client.get_players()
            players = dict(players, **client_players)
        return players

    def client_has_player(self, client_id, player_id):
        client = self.get_client(client_id)
        return client.has_player(player_id)

    def switch_player_team(self, client_id, player_id):
        client = self.get_client(client_id)
        client.switch_player_team(player_id)
        return

    def switch_player_role(self, client_id, player_id):
        client = self.get_client(client_id)
        client.switch_player_role(player_id)
        return

    def delete_player(self, client_id, player_id):
        client = self.get_client(client_id)
        player = client.remove_player(player_id)
        self.used_avatars.remove(player.avatar)
        return

    def client_has_role(self, client_id, team, role):
        client = self.get_client(client_id)
        return client.has_role(team, role)

    def get_player_config_error(self):
        ''' Validate player teams and roles. '''
        teams = {}
        red_roles = {}
        blue_roles = {}

        for player in self.get_players().values():
            teams[player.team] = teams.get(player.team, 0) + 1

            if player.team == PlayerTeam.RED:
                red_roles[player.role] = red_roles.get(player.role, 0) + 1
            elif player.team == PlayerTeam.BLUE:
                blue_roles[player.role] = blue_roles.get(player.role, 0) + 1

        # validate that there are two teams
        if PlayerTeam.RED not in teams:
            return PlayerConfigError.NO_RED_TEAM.value
        if PlayerTeam.BLUE not in teams:
            return PlayerConfigError.NO_BLUE_TEAM.value

        # validate that each team has a spymaster
        if PlayerRole.SPYMASTER not in red_roles:
            return PlayerConfigError.NO_RED_SPYMASTER.value
        if PlayerRole.SPYMASTER not in blue_roles:
            return PlayerConfigError.NO_BLUE_SPYMASTER.value

        # validate that each team has at least one operative
        if PlayerRole.OPERATIVE not in red_roles:
            return PlayerConfigError.NO_RED_OPERATIVE.value
        if PlayerRole.OPERATIVE not in blue_roles:
            return PlayerConfigError.NO_BLUE_OPERATIVE.value

        return PlayerConfigError.NONE.value


    def get_lobby_bundle(self):
        ''' Serializes players to JSON object. '''
        players = self.get_players()
        return {
            'players': [p.serialize() for p in players.values()],
            'errorMessage': self.get_player_config_error()
        }

    def serialize_players(self):
        ''' Serializes players to JSON object. '''
        players = self.get_players()
        return {
            'players': [p.serialize() for p in players.values()],
            'errorMessage': self.get_player_config_error()
        }

    def serialize_players_mapping(self):
        ''' Serializes playerid to player mapping to JSON object. '''
        players = self.get_players()
        print(players)
        return {
            'playersMapping': { pId: p.serialize() for pId, p in players.items() }
        }
