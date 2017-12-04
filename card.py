from enum import Enum

class Card(object):
    ''' Card value class storing codename word, status, and board position.
        The game deck is composed of cards.
    '''

    def __init__(self, word, position):
        # Word assigned to this card
        self.word = word

        # Status of card
        # EMPTY, RED, BLUE, NEUTRAL, BOMB
        self.status = CardStatus.EMPTY

        # Position of card on the board
        self.position = position

    # Getters / setters

    def set_status(self, status):
        assert(status in CardStatus), "Invalid status"
        self.status = status

    def get_status(self):
        return self.status

    def get_word(self):
        return self.word

    def get_position(self):
        return self.position

    def serialize(self):
        ''' Serializes Card word and status to JSON. '''
        return {
            "status": self.status.name,
            "word": self.word
        }

    def __str__(self):
        return "(%s,%s)" % (self.word, self.get_status().name)

class CardStatus(Enum):
    EMPTY = 0
    NEUTRAL = 1
    RED = 2
    BLUE = 3
    BOMB = 4
