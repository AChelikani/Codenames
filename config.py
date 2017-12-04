import json

class Configuration:
    ''' Key-value in-memory configuration object. '''

    def __init__(self, dict):
        self.NUM_CARDS = dict.get("NUM_CARDS", DefaultConfiguration.NUM_CARDS)
        self.NUM_BOMBS = dict.get("NUM_BOMBS", DefaultConfiguration.NUM_BOMBS)
        self.NUM_REDS = dict.get("NUM_REDS", DefaultConfiguration.NUM_REDS)
        self.NUM_BLUES = dict.get("NUM_BLUES", DefaultConfiguration.NUM_BLUES)
        self.GAME_CODE_LEN = dict.get("GAME_CODE_LEN", DefaultConfiguration.GAME_CODE_LEN)
        self.WORDS_FILE = dict.get("WORDS_FILE", DefaultConfiguration.WORDS_FILE)
        self.AVATARS = dict.get("AVATARS", DefaultConfiguration.AVATARS)
        self.CLEAN_UP_DELTA = dict.get("CLEAN_UP_DELTA", DefaultConfiguration.CLEAN_UP_DELTA)

    @classmethod
    def fileConfiguration(cls):
        ''' Creates configuration object from JSON file. '''
        return cls(FileConfiguration.parseConfigDict())

    @staticmethod
    def factory(type):
        ''' Factory method for constructing configuration by type.
            Extensible to other configuration source types.
        '''
        if type == "file":
            return Configuration.fileConfiguration()
        else:
            raise ValueError("Unknown configuration type specified")

    # Getters

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
    ''' Namespace for file configuration related helper methods. '''

    @staticmethod
    def parseConfigDict():
        ''' Parses JSON into python dictionary. '''
        configFilePath = FileConfiguration.getConfigFilePath()
        dict = {}
        with open(configFilePath, 'r') as f:
            dict = json.loads(f.read())
        return dict

    @staticmethod
    def getConfigFilePath():
        ''' Get JSON file path (THIS SHOULD NOT CHANGE TRIVIALLY). '''
        return "resources/config.json"

class DefaultConfiguration:
    ''' Default in-code configuration options (if file is unavailable). '''

    NUM_CARDS = 25
    NUM_BOMBS = 1
    NUM_REDS = 8
    NUM_BLUES = 8
    WORDS_FILE = "resources/words.txt"
    GAME_CODE_LEN = 5
    AVATARS = []
    CLEAN_UP_DELTA = 600
global_config = Configuration.factory("file")
