from config import CardStatus
from config import global_config as config
import random

# Each map card has 1 bomb, 7 neutral, 8 lagging color, 9 starting color
class MapCard(object):
    def __init__(self):
        self.starting_color = random.choice([CardStatus.RED, CardStatus.BLUE])
        self.map = self._gen_map_card()
        self.bomb_location = self.map.index(CardStatus.BOMB)

    def _gen_map_card(self):
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
        return self.starting_color

    def get_bomb_location(self):
        return self.bomb_location

    def get_card_type_at_position(self, position):
        return self.map[position]

    def get_num_card_by_type(self, card_type):
        return self.map.count(card_type)

    # Serialize the map card into JSON
    def serialize(self):
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
