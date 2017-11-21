from config import CardStatus

class Card(object):
    def __init__(self, word, position):
        # Word assigned to this card
        self.word = word

        # Status of card
        # EMPTY, RED, BLUE, NEUTRAL, BOMB
        self.status = CardStatus.EMPTY

        # Position of card on the board
        self.position = position

    def set_status(self, status):
        assert(status in CardStatus), "Invalid status"
        self.status = status

    def get_status(self):
        return self.status

    def get_word(self):
        return self.word

    def get_position(self):
        return self.position

    def __repr__(self):
        return self.word
