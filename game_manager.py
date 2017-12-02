from codename_game import CodenameGame
from codename_client import Client
from codename_player import *
from utils import JSONUtils

class PlayerConfigError(Enum):
    NONE = ''
    NO_RED_TEAM = 'Add a red team to get started.'
    NO_RED_SPYMASTER = 'Red team is missing a spymaster.'
    NO_RED_OPERATIVE = 'Red team is missing an operative.'
    NO_BLUE_TEAM = 'Add a blue team to get started.'
    NO_BLUE_SPYMASTER = 'Blue team is missing a spymaster.'
    NO_BLUE_OPERATIVE = 'Blue team is missing an operative.'    

class GameManager(object):
    def __init__(self, game_code):
        # Game code of game being managed.
        self.game_code = game_code
        # Generated codename game.
        self.game = CodenameGame()
        # Active clients of game.
        self.clients = {}
        # Disconnected clients of game (for in case they come back).
        self.dangling_clients = {}
        # Avatars being used for clients.
        self.used_avatars = []

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
        client = self.get_client(client_id)
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

    # TODO: maybe there's a cleaner solution to this?
    def get_players(self):
        players = {}
        for client in self.clients.values():
            client_players = client.get_players()
            players = JSONUtils.merge(players, client_players)
        return players

    def get_game(self):
        ''' Returns contained CodenamesGame object. '''
        return self.game

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

    def get_client_cookie(self, client_id):
        client = self.get_client(client_id)
        return {
            'client_id': client_id,
        	'players': [p.serialize() for p in client.get_players().values()]
		}

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

    def serialize_game(self):
        ''' Serializes contained game to JSON object along with game code. '''
        game_bundle = self.game.serialize()
        game_bundle['gameCode'] = str(self.game_code)
        return game_bundle

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
        return {
            'players_mapping': [{'playerId': pId, 'player': p.serialize()} for pId, p in players.items()]
        }
