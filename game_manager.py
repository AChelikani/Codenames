from codename_game import CodenameGame
from codename_player import Player, PlayerTeam, PlayerRole

class GameManager(object):
    def __init__(self, game_code):
        # Game code of game being managed.
        self.game_code = game_code
        # Generated codename game.
        self.game = CodenameGame()
        # Active players of game.
        self.players = {}
        # Disconnected players of game (for in case they come back).
        self.dangling_players = {}
        # Avatars being used for players.
        self.used_avatars = []

    def get_num_players(self):
        ''' Returns number of active players. '''
        return len(self.players)

    def add_player(self, player):
        ''' Adds new player to active players and tracks avatar'''
        self.players[player.id] = player
        self.used_avatars.append(player.avatar)
        return player

    def add_new_player(self):
        ''' Creates new player and adds it. '''
        new_player = Player.new_player(self.used_avatars)
        self.add_player(new_player)
        return new_player

    def remove_player(self, player_id):
        ''' Removes player from active players'''
        player = self.players.pop(player_id, None)
        self.used_avatars.remove(player.avatar)
        self.dangling_players[player_id] = player
        return player

    def get_players(self):
        ''' Returns active player id to player mapping. '''
        return self.players

    def get_player(self, player_id):
        ''' Returns corresponding active player if exists else None '''
        if player_id in self.players:
            return self.players[player_id]
        return None

    def get_dangling_players(self):
        ''' Returns disconnectd player id to player mapping. '''
        return self.dangling_players

    def restore_player(self, player_id):
        ''' Restores disconnected player to active player mapping. '''
        player = self.dangling_players.pop(player_id)
        player = Player(player.id, player.team, player.role, Player._get_avatar(self.used_avatars))
        return self.add_player(player)

    def switch_player_team(self, player_id):
        ''' Switches player team (RED/BLUE). '''
        if player_id not in self.players:
            raise ValueError("player id %s not found in players" % player_id)
        player = self.players[player_id]
        player.team = PlayerTeam.BLUE if player.team == PlayerTeam.RED else PlayerTeam.RED
        return

    def switch_player_role(self, player_id):
        ''' Switches player role (PLAYER/SPYMASTER). '''
        player = self.players[player_id]
        player.role = PlayerRole.SPYMASTER if player.role == PlayerRole.PLAYER else PlayerRole.PLAYER

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
        return {
            'players': [p.serialize() for p in self.get_players().values()]
        }

    def serialize_players_mapping(self):
        ''' Serializes playerid to player mapping to JSON object. '''
        return {
            'players_mapping': [{'playerId': pId, 'player': p.serialize()} for pId, p in self.players.items()]
        }
