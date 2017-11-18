import config
import random
from codename_card import *
from map_card import *

class CodenameGame(object):
    def __init__(self):
        # An array of Card objects
        self.deck = self._gen_cards()
        self.map_card = MapCard()
        self.red_count = 0
        self.blue_count = 0

    # Generate a new deck of cards, chosing a set of cards randomly from the set
    # of all cards.
    def _gen_cards(self):
        words = random.sample(config.WORDS, config.NUM_CARDS)
        cards = []
        for word in words:
            cards.append(Card(word))
        return cards

    def mark_card(self, card, new_status):
        card.set_status(new_status)

    def is_game_over(self):
        # Game over condition is that red or blue meets their total possible or the bomb has been hit

        # Check if bomb has been uncovered
        bomb_location = self.map_card.get_bomb_location()
        if (self.deck[bomb_location].get_status() == config.BOMB):
            return True

        # Check if red or blue is at winning count
        if (self.red_count == self.map_card.get_num_card_by_type(config.RED)):
            return True
        elif (self.blue_count == self.map_card.get_num_card_by_type(config.BLUE)):
            return True

        return False


    def __repr__(self):
        output = str(self.map_card) + "\n"
        max_len = 15
        spacer = lambda x: str(x) + " "*(max_len - len(str(x)))
        for x in range(5):
            output += "".join(map(spacer, self.deck[5*x:5*x+5]))
            output += "\n"
        output += "\n"
        status_spacer = lambda x: str(x.status) + " "*(max_len - len(x.status))
        for x in range(5):
            output += "".join(map(status_spacer, self.deck[5*x:5*x+5]))
            output += "\n"
        return output


if __name__ == "__main__":
    cg = CodenameGame()
    #cg.mark_card(cg.deck[0], config.RED)
    print cg
