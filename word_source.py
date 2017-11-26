import random
from config import global_config as config
import nltk
from nltk.corpus import wordnet as wn

class WordsSource:

	def sampleWords(n):
		raise NotImplementedError("Please Implement this method")

class WordsFile:

	def __init__(self, filename):
		self.filename = filename

	def getAllWords(self):
		words = []
		with open(self.filename, 'r') as f:
			for line in f:
				words.append(line.strip().lower())
		return words

class WordsFromFile(WordsSource):

	def __init__(self):
		self._words = None
		self._wordsFile = WordsFile(config.WORDS_FILE)

	def getAllWords(self):
		if self._words is None:
			self._words = self._wordsFile.getAllWords()
		return self._words

	def refreshWords(self):
		self._words = self._wordsFile.getAllWords()

	def sampleWords(self,n):
		words = self.getAllWords()
		return random.sample(words, n)
	
class NounsFromNLTK(WordsSource):

	def __init__(self):
		self._words = None

	def getAllWords(self):
		if self._words is None:
			_words = self.getSingleWordNouns()
		return _words

	def getSingleWordNouns(self):
		nltk.download('wordnet')
		nouns = set()
		for synset in wn.all_synsets(wn.NOUN):
			lemma_names = synset.lemma_names()
			for name in lemma_names:
				try:
					ascii_name = name.encode('ascii')		
					if ascii_name.count('_') > 0:
						continue
					else:
						nouns.add(ascii_name)
				except UnicodeEncodeError:
					continue
		return list(nouns)
	
	def refreshWords(self):
		self._words = self.getSingleWordNouns()

	def sampleWords(self,n):
		words = self.getAllWords()
		return random.sample(words, n)

# For global access
WordsInMemory = WordsFromFile()

# Take input list of words from file
# Use concept.io to build graph (in-memory)
#	word relations, where words are nodes, and
# 	relations are edges
# Sample graph to find superset (of independent set of size k) 
# 	which is of requisite size n.
# class WordsFromNounsGraph(WordsSource):

		
# Utility functions

def reservoirSample(iterator, K):
	result = []
	N = 0

	for item in iterator:
	    N += 1
	    if len( result ) < K:
	        result.append( item )
	    else:
	        s = int(random.random() * N)
	        if s < K:
	            result[ s ] = item

	return result	

# Default values

DEFAULT_WORDS = [
        "Europe",
        "Cat",
        "Bermuda",
        "Jupiter",
        "Dance",
        "Pupil",
        "Mail",
        "Fair",
        "Germany",
        "Forest",
        "Thumb",
        "Press",
        "Snow",
        "Day",
        "Washington",
        "Fly",
        "Head",
        "Dog",
        "Iron",
        "Train",
        "Beat",
        "Nail",
        "Charge",
        "Bell",
        "Alps"
    ]