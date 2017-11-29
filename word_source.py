import random
from config import global_config as config
import nltk
from nltk.corpus import wordnet as wn

class WordsSource:
	'''	Interface defining required methods of a word source. '''

	def sampleWords(n):
		''' Sample `n` words from the word source. This sampling may be random
			or biased in ways to improve content-distibution of words.
		'''
		raise NotImplementedError("Please Implement this method")

class WordsFile:
	'''	Wrapper on file containing newline separated list of words. '''
	def __init__(self, filename):
		self.filename = filename

	def getAllWords(self):
		''' Fetches all words in file as in-memory list. '''
		words = []
		with open(self.filename, 'r') as f:
			for line in f:
				words.append(line.strip().lower())
		return words

class WordsFromFile(WordsSource):
	''' Word source based off of file containing newline separated list of words. '''
	def __init__(self):
		# In-memory list of words in file.
		self._words = None
		# Wrapper around file containing word list.
		self._wordsFile = WordsFile(config.WORDS_FILE)

	def getAllWords(self):
		'''	Lazily evaluated/cached method that returns stored list of all words in file. '''
		if self._words is None:
			self._words = self._wordsFile.getAllWords()
		return self._words

	def refreshWords(self):
		''' Force-refreshes in-memory list of words. '''
		self._words = self._wordsFile.getAllWords()

	def sampleWords(self,n):
		''' Samples words uniformly from in-memory word list (of file contents). '''
		words = self.getAllWords()
		return random.sample(words, n)
	
class NounsFromNLTK(WordsSource):
	''' Word source based off WordNet english word synset index. '''
	def __init__(self):
		self._words = None

	def getAllWords(self):
		'''	Lazily evaluated/cached method that returns stored list of all single-word nouns in WordNet. '''
		if self._words is None:
			_words = self.getSingleWordNouns()
		return _words

	def getSingleWordNouns(self):
		'''	Helper method of `getAllWords()` that fetches all single-word nouns in WordNet. '''
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
		''' Force-refreshes in-memory list of words. '''
		self._words = self.getSingleWordNouns()

	def sampleWords(self,n):
		''' Samples words uniformly from in-memory word list (of single-word nouns). '''
		words = self.getAllWords()
		return random.sample(words, n)

# For global access
WordsInMemory = WordsFromFile()

"""
Possible advanced game generation technique (for future):
# Take input list of words from file
# Use concept.io to build graph (in-memory)
#	word relations, where words are nodes, and
# 	relations are edges
# Sample graph to find superset (of independent set of size k) 
# 	which is of requisite size n.

"""
	
# Utility functions

def reservoirSample(iterator, K):
	''' Implements reservoir sampling for performing random sampling from a stream of items. 
		Currently unused, may be used in the future.
	'''
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