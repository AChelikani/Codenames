from enum import Enum
import json

class CardStatus(Enum):
    EMPTY = 0
    NEUTRAL = 1
    RED = 2
    BLUE = 3
    BOMB = 4

class Configuration:

    def __init__(self, dict):
        self.NUM_CARDS = dict.get("NUM_CARDS", DefaultConfiguration.NUM_CARDS)
        self.NUM_BOMBS = dict.get("NUM_BOMBS", DefaultConfiguration.NUM_BOMBS)
        self.NUM_REDS = dict.get("NUM_REDS", DefaultConfiguration.NUM_REDS)
        self.NUM_BLUES = dict.get("NUM_BLUES", DefaultConfiguration.NUM_BLUES)
        self.GAME_CODE_LEN = dict.get("GAME_CODE_LEN", DefaultConfiguration.GAME_CODE_LEN)
        self.WORDS_FILE = dict.get("WORDS_FILE", DefaultConfiguration.WORDS_FILE)
        self.AVATARS = dict.get("AVATARS", DefaultConfiguration.AVATARS)

    @classmethod
    def fileConfiguration(cls):
        return cls(FileConfiguration.parseConfigDict())

    @staticmethod
    def factory(type):
        if type == "file":
            return Configuration.fileConfiguration()
        else:
            raise ValueError("Unknown configuration type specified")

    def getNumCards(self):
        return self.NUM_CARDS

    def getNumBombs(self):
        return self.NUM_BOMBS

    def getNumReds(self):
        return self.NUM_REDS

    def getNumBlues(self):
        return self.NUM_BLUES

    def getNumNeutrals(self):
        return self.NUM_CARDS - self.NUM_BOMBS - self.NUM_REDS - self.NUM_BLUES

    def getGameCodeLen(self):
        return self.GAME_CODE_LEN

    def getAvatars(self):
        return self.AVATARS

class FileConfiguration:

    @staticmethod
    def parseConfigDict():
        configFilePath = FileConfiguration.getConfigFilePath()
        dict = {}
        with open(configFilePath, 'r') as f:
            dict = json.loads(f.read())
        return dict

    @staticmethod
    def getConfigFilePath():
        return "resources/config.json"

class DefaultConfiguration:

    NUM_CARDS = 25
    NUM_BOMBS = 1
    NUM_REDS = 8
    NUM_BLUES = 8
    WORDS_FILE = "resources/words.txt"
    GAME_CODE_LEN = 5
    AVATARS_FILE = "resources/avatars.txt"
    AVATARS = []
global_config = Configuration.factory("file")
