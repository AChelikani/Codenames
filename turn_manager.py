from transitions import Machine
from enum import Enum
from player import PlayerRole, PlayerTeam

'''
class PlayerRole(Enum):
    RED_SPYMASTER = 'Red Spymaster'
    RED_OPERATIVE = 'Red Operative'
    BLUE_SPYMASTER = 'Blue Spymaster'
    BLUE_OPERATIVE = 'Blue Operative'
'''

red = PlayerTeam.RED.value + ' '
blue = PlayerTeam.BLUE.value + ' '
spymaster = PlayerRole.SPYMASTER.value
operative = PlayerRole.OPERATIVE.value

red_spymaster = red + spymaster
red_operative = red + operative
blue_spymaster = blue + spymaster
blue_operative = blue + operative

class TurnManager(object):
    states = [red_spymaster, red_operative, blue_spymaster, blue_operative]
    transitions = [
        ['next_turn', red_spymaster, red_operative],
        ['next_turn', red_operative, blue_spymaster],
        ['next_turn', blue_spymaster, blue_operative],
        ['next_turn', blue_operative, red_spymaster],
    ]

    def __init__(self, starting_team):
        starting_role = PlayerRole.SPYMASTER
        self.machine = Machine(
            model=self,
            states=TurnManager.states,
            initial=TurnManager.create_state(starting_team, starting_role)
        )

    @staticmethod
    def create_state(team, role):
        return team.value + ' ' + role.value

    def get_current_turn(self):
        return self.state

    def get_current_turn_team_role(self):
        team_raw, role_raw = self.state.split()
        return PlayerTeam(team_raw), PlayerRole(role_raw)
