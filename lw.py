import json
import os, sys

alphabet = [l for l in 'abcdefghijklmnopqrstuvwxyz']

def new_level():
    return dict(zip(alphabet, [[] for n in alphabet]))
    #{'a': [], 'b': [], 'c': [], 'd': [], 'e': [], ....

testwords = list(set('wikipedia is a free online encyclopedia with the aim to allow anyone to edit articles wikipedia is the largest and most popular general reference work on the internet and is ranked the fifth most popular website'.split(' ')))


class Trie:
    DEBUG = False
    def __init__(self, words):
        self.max_length = max([len(w) for w in words])
        self.layers = dict(zip(range(1, self.max_length+1), [new_level() for n in range(self.max_length)]))
        # {1: {'a':[], 'b': [], 'c': [] ...}, 2: {'a': [], 'b': [], ...}, ...}
        
        for word in words:
            for i in range(len(word)):
                try:
                    if Trie.DEBUG:
                        print 'adding word "{}" to layer {} under "{}"'.format(word, i+1, word[i])
                    self.layers[i+1][word[i]].append(word)
                except Exception as e:
                    if Trie.DEBUG:
                        print '{}\n{}\n{}\n'.format(e, word[i], word)
                    break

    def search(self, *kw):
        pass

t = Trie(testwords)

def load_words():
    filename = "words_dictionary.json"
    with open(filename,"r") as english_dictionary:
        valid_words = json.load(english_dictionary)
        return valid_words.keys()

