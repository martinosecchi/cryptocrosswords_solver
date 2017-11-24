import json
import os, sys

alphabet = [l for l in 'abcdefghijklmnopqrstuvwxyz']


testwords = list(set('hello wikipedia is a free online encyclopedia with the aim to allow anyone to edit articles wikipedia is the largest and most popular general reference work on the internet and is ranked the fifth most popular website'.split(' ')))


class LeveledList(object):
    def __init__(self, words):
        self.max_length = max([len(w) for w in words])
        self.layers = dict(zip(range(1, self.max_length+1), [self.new_level_full() for n in range(self.max_length)]))
        # {1: {'a':[], 'b': [], 'c': [] ...}, 2: {'a': [], 'b': [], ...}, ...}
        
        for word in words:
            for i in range(len(word)):
                try:
                    self.layers[i+1][word[i]].append(word)
                except Exception as e:
                    break
    
    def new_level_full(self):
        return dict(zip(alphabet, [[] for n in alphabet]))
        #{'a': [], 'b': [], 'c': [], 'd': [], 'e': [], ....

    def search(self, length, *kw):
        pass


class Node(object):
    def __init__(self):
        self.children = {}
        self.words = {}
        self.lengths = {}
    def has_words(self):
        return len(self.words) > 0
    def __str__(self):
        return str(self.children.keys()) + "\n" + str(self.words.keys()) + "\n" + str(self.lengths)

class Trie(object):
    def __init__(self, words):
        self.max_length = max([len(w) for w in words])
        self.layers = dict(zip(range(1, self.max_length+1), [Node() for n in range(self.max_length)]))
        # {1: root, 2: root, 3: root, ...}
        print 'loading words..'
        n = 0.0
        N = len(words)
        for word in words:
            sys.stdout.write('%3d %%\r'%(int(n/N*100)))
            sys.stdout.flush()
            n+=1
            for i in range(len(word)):
                self.insert(i+1, word[i:], word)
        print 'done.'

    def insert(self, layer, letters, word):
        node = self.layers[layer]
        for l in letters:
            if not node.children.get(l):
                node.children[l] = Node()
            if node.lengths.has_key(len(word)):
                if l not in node.lengths[len(word)]:
                    node.lengths[len(word)].append(l)
            else:
                node.lengths[len(word)] = [l]
            node = node.children[l]
        node.words[word] = word  

tf = LeveledList(testwords)
t = Trie(testwords)

def load_words():
    filename = "words_dictionary.json"
    with open(filename,"r") as english_dictionary:
        valid_words = json.load(english_dictionary)
        return valid_words.keys()

