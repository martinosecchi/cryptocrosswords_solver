#!/usr/bin/python
#coding: utf-8 
from __future__ import print_function
import json
import os, sys
import re
from logger import logapp
from Queue import LifoQueue as Stack

alphabet = [l for l in 'abcdefghijklmnopqrstuvwxyz']
testwords = list(set('hello callo bollo messo tetto wikipedia is a free online encyclopedia with the aim to allow anyone to edit articles wikipedia is the largest and most popular general reference work on the internet and is ranked the fifth most popular website'.split(' ')))

class Node(object):
    def __init__(self):
        self.children = {}
        self.words = set()
        self.lengths = {}
        self.level = -1
    def has_words(self):
        return len(self.words) 
    def __str__(self):
        return str(self.level) + '\n' + str(self.children.keys()) + "\n" + str(self.words) + "\n" + str(self.lengths)

class Trie(object):
    def __init__(self, words):
        self.max_length = max([len(w) for w in words])
        self.layer = dict(zip(range(self.max_length), [Node() for n in range(self.max_length)]))
        # {1: root, 2: root, 3: root, ...}
        print('loading words from dictionary..')
        n = 0.0
        N = len(words)
        for word in words:
            sys.stdout.write('%4d %%\r'%(int(n/N*100)))
            sys.stdout.flush()
            n+=1
            for i in range(len(word)):
                self.insert(i, word[i:], word)
        print('done loading dictionary.')

    def insert(self, layer, letters, word):
        node = self.layer[layer]
        i = 0
        for l in letters:
            if not node.children.get(l):
                node.children[l] = Node()
                node.level = i + layer 
            i+=1
            if node.lengths.has_key(len(word)):
                if l not in node.lengths[len(word)]:
                    node.lengths[len(word)].append(l)
            else:
                node.lengths[len(word)] = [l]
            node = node.children[l]
        node.words.update([word])
        node.level = len(word)

    def search_word(self, word):
        node = self.layer[0]
        for i in range(len(word)):
            if node.lengths.has_key(len(word)) and word[i] in node.lengths[len(word)]:
                node = node.children[word[i]]
            else:
                return False
        return word in node.words

    def search_pattern(self, pattern):
        logapp('DEBUG', 'Searching for pattern ' + str(pattern))
        has_letters = pattern.has_letters()
        if has_letters:
            # take the letters, and positions. then start searching from the layer corresponding to the first position
            # extensive search of all the children at least until the next known position in the word, but only from the ones who
            # lead to a word of the desired size
            # in the end, check all the words I find with pattern.check
            return self._searchp_with_letters(pattern, has_letters)
        else:
            # best avoid, this might as well be linear search.
            # look if there are repetitions of letters and their positions, then look in the different layers at the corresponding positions
            # test the pattern on those words that have the right length
            # (set operations)
            # I can create a new pattern for every possibility I find and give it some letters, then do the letter search
            # e.g. if I get 1,2,1,1,3 of length 5, I look in layer 0 what letters go to 5, then create a pattern for each letter
            # BUT only if that letter is also in the other layers where it's supposed to be (constant time lookup)
            # Pattern([1,2,1,1,3], {1: letter}) and search for that
            # could do this for the most common letter, and then check the pattern
            # is there a more efficient way? probably
            pass

    def _searchp_with_letters(self, p, has_letters):
        indexes, letters = p.get_letters_at_positions()
        words = set()
        s = Stack()
        i = 0
        s.put(self.layer[indexes[i]].children[letters[i]])
        has_letters += -1
        i += 1

        # DFS
        while not s.empty():
            node = s.get_nowait()
            logapp('DEBUG', str(node))
            # need to know which level we at, so I can compare also the other indexes/letters and check for words
            if node.level == p.length:
                # get me those words son
                logapp('DEBUG', 'Adding words if they match: ' + str(node.words))
                for word in node.words:
                    if p.check(word):
                        words.update([word])
            elif node.lengths.has_key(p.length):
                if has_letters and node.level == indexes[i]:
                    logapp('DEBUG', 'we are at next letter in pattern: ' + letters[i])
                    #are we at level of next letter?
                    # put only the child that checks with the next letter
                    # BUT only if it goes to a word of the right length
                    if letters[i] in node.lengths[p.length]:
                        s.put(node.children[letters[i]])
                        logapp('DEBUG', 'there is a path from here, adding child.')
                    i += 1
                    has_letters += -1
                else:
                    # put all the childs that go to a word of the right length
                    logapp('DEBUG', 'Adding all children.')
                    for child in node.lengths[p.length]:
                        s.put(node.children[child])
        return words

class Pattern(object):
    def __init__(self, array, solution):
        self.array_form = array # only numbers
        self.solution = solution # shared object
        self.length = len(self.array_form)
        self._letter = re.compile(r'^[a-z]{1}$')
        self._number = re.compile(r'^[0-9]{1,2}$')
    def __str__(self):
        return ','.join([x if not self.solution.get(x) else self.solution[x] for x in self.array_form])
    def get_letters_at_positions(self):
        indexes = []
        letters = []
        for i in range(len(self.array_form)):
            if self.solution.get(self.array_form[i]):
                indexes.append(i)
                letters.append(self.solution.get(self.array_form[i]))
        return indexes, letters
    def has_letters(self):
        letters = 0
        for x in self.array_form:
            if self._isletter(self.solution.get(x) or '1'):
                letters += 1
        return letters
    def _isletter(self, x):
        return self._letter.match(x) is not None
    def _isnumber(self, x):
        return self._number.match(x) is not None
    def _validate(self, word):
        for l in word:
            if not self._isletter(l):
                return False
        return True
    # ['1', '2', 'l', 'l', '3'] # matches for hello, not collo
    def check(self, word): # checks a word on this pattern
        if len(word) != len(self.array_form):
            return False
        if self._validate(word):
            testword = self.array_form[:]
            testsolution = {}
            for i in range(len(word)):
                x = self.solution.get(testword[i]) or testword[i]
                if self._isnumber(x):
                    if testsolution.has_key(x):
                        testword[i] = testsolution[x]
                    elif word[i] not in testsolution.values():
                        testsolution[x] = word[i]
                        testword[i] = word[i]
                    else:
                        return False
                elif self._isletter(x):
                    testword[i] = x
            logapp('DEBUG', 'testing word {} - reconstructed as: {} testsolution {}'.format(word, testword, testsolution))
            if  ''.join(testword) == word :
                return testsolution
        return False

def load_english(filename="words_dictionary.json"):
    with open(filename,"r") as english_dictionary:
        valid_words = json.load(english_dictionary)
        return valid_words.keys()
def load_italian(filename="parole.txt"):
    lines = []
    with open(filename, "r") as f:
        for line in f:
            try:
                word = line.decode('utf8')
                word = word.replace(u'à', 'a')
                word = word.replace(u'á', 'a')
                word = word.replace(u'è', 'e')
                word = word.replace(u'é', 'e')
                word = word.replace(u'í', 'i')
                word = word.replace(u'ì', 'i')
                word = word.replace(u'ò', 'o')
                word = word.replace(u'ó', 'o')
                word = word.replace(u'ù', 'u')
                word = word.replace(u'ú', 'u')
                for l in word:
                    if l not in alphabet + ['\n']:
                        raise Exception(l.decode('utf8') + u' - not in alphabet')
                lines.append(word.rstrip('\n').encode('utf8'))
            except Exception as e:
                logapp('ERROR', 'unicode error: ' + line.rstrip('\n') + ' ' + str(e))
    return lines


class Solver(object):
    def __init__(self, dictionary, inputfn):
        self.t = Trie(load_italian(dictionary))
        self.patterns = []
        self.hints = {}
        self.solution = {}  #dict(zip(map(lambda x: str(x), range(1,len(alphabet)+1)),map(lambda x: str(x), range(1,len(alphabet)+1)) ))
                            # {'1':'1', '2':'2', ...}
        self._possible_vowels = []
        self._possible_letters = {}

    def _is_vowel(self, letter):
        return letter in 'aeiou'

    def parse_input(self ):
        filename = "input.txt"
        lines = []
        hints = {}
        with open(filename, "r") as f:
            n = int(f.readline())
            m = int(f.readline())
            for i in range(m):
                lines.append(f.readline().split(','))
            while True:
                line = f.readline()
                if not line:
                    break
                k,v = line.split(',')
                hints[k] = v.rstrip('\n')
        self._validate(lines, n, m)
        return self._flatten(lines,n,m), hints

    def _validate(self, lines, n, m):
        pattern = re.compile(r'^[_]{1}|[0-9]{1,2}$')
        try:
            assert len(lines) == m
            for l in lines:
                assert len(l) == n
                for e in range(len(l)):
                    l[e] = l[e].rstrip('\n')
                    assert pattern.match(l[e]) is not None
        except AssertionError as ae:
            logapp('ERROR', 'Error in input: validate failed. ' + str(ae))

    def _flatten(self, square, n, m):
        patterns = []
        # # horizontal
        for i in range(n):
            word = []
            for j in range(m):
                word.append(square[i][j]) if square[i][j] != '_' else None
                if square[i][j] == '_' or j == m-1:
                    patterns.append(word) if len(word) > 1 else None
                    word = []
        # vertical
        for j in range(m):
            word = []
            for i in range(n):
                word.append(square[i][j]) if square[i][j] != '_' else None
                if square[i][j] == '_' or i == n-1:
                    patterns.append(word) if len(word) > 1 else None
                    word = []
        return patterns

    def _create_patterns(self, arrays):
        for a in arrays:
            self.patterns.append(Pattern(a, self.solution))

    def solve(self):
        pattern_arays, self.hints = self.parse_input(inputfn)
        for k,v in self.hints.items():
            self.solution[k] = v
        self._create_patterns(pattern_arays)
        # ....