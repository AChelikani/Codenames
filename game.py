from card import Card, CardStatus
from config import global_config as config
from copy import deepcopy
from enum import Enum
from map_card import *
from player import PlayerTeam
from transitions import Machine
from turn_manager import TurnManager
from word_source import WordsInMemory


class GameEvent(Enum):
    TURN = 'game_turn'
    STOP = 'game_stop'
    PAUSE = 'game_pause'
    CHOOSE_WORD = 'choose_word'
    SUBMIT_CLUE = 'submit_clue'
    UPDATE = 'game_update'


class CodenameGame(object):
    ''' CodenameGame contains a representation of the game board, as players
        see it.
    '''

    def __init__(self):
        # An array of Card objects. The elements composing the deck do not ever change
        #   although the elements themselves are mutated as the game progresses.
        self.deck = self._gen_cards()
        # Solution mapping of actual card statuses (Immutable).
        self.map_card = MapCard()
        # Number of 'found' red cards (Mutable).
        self.red_count = 0
        # Number of 'found' blue cards (Mutable).
        self.blue_count = 0
        # Current turn (RED/BLUE) as a CardStatus (Mutable).
        self.starting_team = self.map_card.get_starting_color()
        # Current turn clue (Mutable).
        self.current_clue = None
        # Log of each turn's clue, guesses, and results (Mutable).
        self.activity_log = ActivityLog()
        # Mutable buffer for building activity log entries.
        self.log_entry_builder = LogEntryBuilder()
        # Create a new turn manager with the starting color
        self.turn_manager = TurnManager(self.starting_team)

    # Generate a new deck of cards, chosing a set of cards randomly from the set
    # of all cards.
    def _gen_cards(self):
        ''' Generate a set of word cards '''
        words = WordsInMemory.sampleWords(config.getNumCards())
        cards = []
        position = 0
        for word in words:
            cards.append(Card(word, position))
            position += 1
        return cards

    def handle_game_event(self):
        pass

    def mark_card(self, ind, new_status):
        ''' Mark a card as either red or blue, based on the passed in status. '''
        assert(0 <= ind < len(deck))
        self.deck[ind].set_status(new_status)

    def get_card_by_word(self, word):
        ''' Get a card object from the board given a word '''
        for card in self.deck:
            if (card.get_word() == word):
                return card
        return None

    def set_current_clue(self, word, number):
        ''' Set the current clue that the spymaster has given '''
        assert(int(number) == number), "Not a valid number"

        self.current_clue = Clue(word, number)
        self.turn_manager.next_turn()

    # Makes a guess, and returns boolean based on correctness of guess
    def make_guess(self, word):
        ''' Represents the player making a guess by selecting a specific word '''
        if (self.current_clue is None):
            raise Exception("No clue given")

        if (self.current_clue.number == 0):
            raise Exception("No more guesses left!")

        card = self.get_card_by_word(word)
        if (not card):
            raise Exception("Invalid word")

        team, role = self.get_current_turn()
        position_type = self.map_card.get_card_type_at_position(card.get_position())
        self.log_entry_builder.track_guess(Card(word, position_type))
        if (team.name == position_type.name):
            card.set_status(position_type)
            self.current_clue.number -= 1
        else:
            # Incorrect guess ends the turn
            card.set_status(position_type)
            self.current_clue.number = 0

        if self.current_clue.number == 0:
            self.turn_manager.next_turn()

    def switch_turns(self, word, number):
        ''' Swtich active turn to the other team '''
        self.log_entry_builder.track_clue(self.side)
        self.log_entry_builder.track_clue(self.clue)
        self.activity_log.addEntry(self.log_entry_builder.build(self.side, self.clue))
        self.current_turn = CardStatus.RED if self.current_turn == CardStatus.BLUE else CardStatus.BLUE
        self.set_current_clue(word, number)

    def get_current_turn(self):
        return self.turn_manager.get_current_turn_team_role()

    def is_game_over(self):
        ''' Check if the game is over by checking the counts of red and blue
            and checking if the bomb was clicked. Game over condition is that
            red or blue meets their total possible or the bomb has been hit.
        '''

        if (
                # Check if bomb has been uncovered.
                self.deck[self.map_card.get_bomb_location()].get_status == CardStatus.BOMB or \
                # Check if red or blue is at winning count.
                self.red_count == self.map_card.get_num_card_by_type(CardStatus.RED) or \
                self.blue_count == self.map_card.get_num_card_by_type(CardStatus.BLUE)
            ):
            # If game is over, update activity log, since no switch-turn will be called.
            self.log_entry_builder.track_clue(self.side)
            self.log_entry_builder.track_clue(self.clue)
            self.activity_log.add_entry(self.log_entry_builder.build(self.side, self.clue))
            return True

        return False

    # Stores the current game state into a JSON
    def serialize(self):
        ''' Serialize the game board, along with card counter, and activity log. '''
        card_statuses = []
        for card in self.deck:
            card_statuses.append(card.get_status())
        serialized_deck = [card.serialize() for card in self.deck]
        team, role = self.get_current_turn()
        return {
            "deck" : serialized_deck,
            "redCount": self.red_count,
            "blueCount": self.blue_count,
            "currentClue": Clue.serialize_clue(self.current_clue),
            "currentTeam": team.value,
            "currentRole": role.value,
            "activityLog": self.activity_log.serialize()
        }

    def __repr__(self):
        output = str(self.map_card) + "\n"
        max_len = 15
        spacer = lambda x: str(x) + " "*(max_len - len(str(x)))
        for x in range(5):
            output += "".join(map(spacer, self.deck[5*x:5*x+5]))
            output += "\n"
        output += "\n"
        status_spacer = lambda x: str(x.status.name) + " "*(max_len - len(x.status.name))
        for x in range(5):
            output += "".join(map(status_spacer, self.deck[5*x:5*x+5]))
            output += "\n"
        return output

class ActivityLog:
    ''' Log of each turn's clue, guesses, and results.
        Stores log entries of turn's side, guesses, and results.
        Essentially a list wrapper with a defined serialize method.
    '''

    def __init__(self, log = []):
        self.log = []

    def add_entry(self, entry):
        ''' Appends new entry to end of list.'''
        self.log.append(entry)

    def serialize(self):
        ''' Serializes log to JSON list of log entries. '''
        return {
            "log": [entry.serialize() for entry in self.log]
        }

class LogEntry:
    ''' Log entry storing clue, side, guesses taken, and number of correct/incorrect. '''

    def __init__(self, clue, side, guesses, numCorrect, numIncorrect):
        self.clue = clue
        self.side = side
        self.guesses = guesses
        self.numCorrect = numCorrect
        self.numIncorrect = numIncorrect

    def serialize(self):
        ''' Serializes all entry field values to JSON. '''
        return {
            "clue": self.clue.serialize(),
            "side": self.side.name,
            "guesses": [card.serialize() for card in self.guesses],
            "numCorrect": str(self.numCorrect),
            "numIncorrect": str(self.numIncorrect)
        }

class LogEntryBuilder:
    ''' Mutable buffer for building `LogEntry` objects for the `ActivityLog`. '''

    def __init__(self):
        self.tracked_guesses = []
        self.side = None
        self.clue = None

    # Tracking methods that store attribute in buffer.

    def track_side(self, side):
        self.side = side

    def track_clue(self, clue):
        self.clue = clue

    def track_guess(self, card):
        self.tracked_guesses.append(card)

    def clear_tracking(self):
        ''' Clears all stored attributes. '''
        self.side = None
        self.clue = None
        self.tracked_guesses = []

    def build(self):
        ''' Builds stored attributes into a log entry AND clears all stored attributes. '''
        numCorrect = 0
        numIncorrect = 0
        for guess in self.tracked_guesses:
            if guess.status == guess.side:
                numCorrect += 1
            else:
                numIncorrect += 1
        entry = LogEntry(side, clue, deepcopy(self.tracked_guesses), numCorrect, numIncorrect)

        entry.clearTracking()
        return entry

class Clue:
    ''' Mutable value class storing given clue word (hint) and number. '''

    def __init__(self, word, number):
        self.word = word
        self.number = number

    def serialize(self):
        ''' Serializes all clue field values to JSON. '''
        return {
            "word": self.word if self.word is not None else "",
            "number": str(self.number) if self.number is not None else ""
        }

    @staticmethod
    def serialize_clue(clue):
        ''' Wrapper method for serializing clue objects to JSON with None handling. '''
        if clue is None:
            return {
                "word": "",
                "number": ""
            }
        else:
            return clue.serialize()
