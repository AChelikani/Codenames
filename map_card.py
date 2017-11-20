import config
import random

# Each map card has 1 bomb, 7 neutral, 8 lagging color, 9 starting color
class MapCard(object):
    def __init__(self):
        self.starting_color = random.choice([config.RED, config.BLUE])
        self.map = self._gen_map_card()
        self.bomb_location = self.map.index(config.BOMB)

    def _gen_map_card(self):
        # TODO: This generation logic needs to be changed
        # It is very hard to remember a random set of 8 or 9 squares on a 25 square grid
        # Rather, it is significantly easier to remember when the squares are in contiguous blobs
        # or have some pattern to them

        assert(config.NUM_CARDS == config.NUM_REDS + config.NUM_BLUES + config.NUM_BOMBS + config.NUM_NEUTRALS + 1), "Invalid config for starting number of each card type"
        mapping = []

        # Add bombs, reds, blues, and neutrals
        for bomb in range(config.NUM_BOMBS):
            mapping.append(config.BOMB)

        for red in range(config.NUM_REDS):
            mapping.append(config.RED)

        for blue in range(config.NUM_BLUES):
            mapping.append(config.BLUE)

        for neutral in range(config.NUM_NEUTRALS):
            mapping.append(config.NEUTRAL)

        # Add one extra for starting color
        mapping.append(self.starting_color)

        # Randomize ordering
        random.shuffle(mapping)

        return mapping

    def get_starting_color(self):
        return self.starting_color

    def get_bomb_location(self):
        pass

    def get_card_type_at_position(self, position):
        return self.map[position]

    def get_num_card_by_type(self, card_type):
        return self.map.count(card_type)

    def __repr__(self):
        output = ""
        max_len = 15
        spacer = lambda x: x + " "*(max_len - len(x))
        for x in range(5):
            output += "".join(map(spacer, self.map[5*x:5*x+5]))
            output += "\n"
        return output
