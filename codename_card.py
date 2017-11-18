import config

class Card(object):
    def __init__(self, word):
        # Word assigned to this card
        self.word = word

        # Status of card
        # EMPTY, RED, BLUE, NEUTRAL, BOMB
        self.status = config.EMPTY

    def set_status(self, status):
        assert(status in config.CARD_STATUSES), "Invalid status"
        self.status = status

    def get_status(self):
        return self.status

    def get_word(self):
        return self.word

    def __repr__(self):
        return self.word
