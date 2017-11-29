from config import CardStatus
from config import global_config as config
import random

# Each map card has 1 bomb, 7 neutral, 8 lagging color, 9 starting color
class MapCard(object):
    ''' A MapCard that holds the information the Spymaster sees.
        - Bomb locations, neutral locations, blue locations, red locations
        Note: the map is visually represented as an n x n grid, but is
        programatically represented as a 1D array.
    '''
    def __init__(self):
        self.starting_color = random.choice([CardStatus.RED, CardStatus.BLUE])
        self.map = self._gen_map_card()
        self.bomb_location = self.map.index(CardStatus.BOMB)

    def _gen_map_card(self):
        ''' Generate a MapCard by random placing the desired entities on a grid
            of the desired size, as passed in from config.
        '''
        # TODO: This generation logic needs to be changed
        # It is very hard to remember a random set of 8 or 9 squares on a 25 square grid
        # Rather, it is significantly easier to remember when the squares are in contiguous blobs
        # or have some pattern to them.

        mapping = []

        # Add bombs, reds, blues, and neutrals
        for bomb in range(config.getNumBombs()):
            mapping.append(CardStatus.BOMB)

        for red in range(config.getNumReds()):
            mapping.append(CardStatus.RED)

        for blue in range(config.getNumBlues()):
            mapping.append(CardStatus.BLUE)

        for neutral in range(config.getNumNeutrals()):
            mapping.append(CardStatus.NEUTRAL)

        # Randomize ordering
        random.shuffle(mapping)

        return mapping

    def get_starting_color(self):
        ''' Get the color of the team whose turn it is first'''
        return self.starting_color

    def get_bomb_location(self):
        ''' Get the location of the bomb on the map'''
        return self.bomb_location

    def get_card_type_at_position(self, position):
        ''' Get the type of card at a given position on the map '''
        return self.map[position]

    def get_num_card_by_type(self, card_type):
        ''' Get the number of a certain type of card on the map '''
        return self.map.count(card_type)

    # Serialize the map card into JSON
    def serialize(self):
        ''' Serialize the data in the MapCard '''
        return {
            "starting_color": self.starting_color.name,
            "map": [str(status.name) for status in self.map],
            "bomb_location": self.bomb_location
        }

    def __repr__(self):
        output = ""
        max_len = 15
        spacer = lambda x: x.name + " "*(max_len - len(x.name))
        for x in range(5):
            output += "".join(map(spacer, self.map[5*x:5*x+5]))
            output += "\n"
        return output
