#!/usr/bin/python
#coding: utf-8 
from __future__ import print_function
import json
import os, sys
import re
from logger import logapp
from Queue import LifoQueue as Stack, PriorityQueue, Queue

alphabet = [l for l in 'abcdefghijklmnopqrstuvwxyz']
testwords = 'hello callo bollo messo tetto'.split(' ')
testdict = 'cassetta aria meg cain denso caro amori male sei ago crac nonnulla cameraman ares mago sig colon sa dare ceri teano erl tris real agnostica'.split(' ')

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
            # to make it a bit better:
            # look if there are repetitions of letters and their positions, then look in the different layers at the corresponding positions
            # test the pattern on those words that have the right length
            # (set operations)
            # I can create a new pattern for every possibility I find and give it some letters, then do the letter search
            # e.g. if I get 1,2,1,1,3 of length 5, I look in layer 0 what letters go to 5, then create a pattern for each letter
            # BUT only if that letter is also in the other layers where it's supposed to be (constant time lookup)
            # Pattern([1,2,1,1,3], {1: letter}) and search for that
            # could do this for the most common letter, and then check the pattern
            # is there a more efficient way? probably
            counts = dict([(e, pattern.array_form.count(e)) for e in pattern.array_form])
            most_occ = counts.keys()[counts.values().index(max(counts.values()))]
            logapp('DEBUG', 'most frequent symbol: ' + most_occ)
            positions = [ i for i in range(pattern.length) if pattern.array_form[i] == most_occ]
            possible_letters = set([])
            for pos in positions:
                if possible_letters == set([]):
                    possible_letters = set(self.layer[pos].lengths[pattern.length])
                else:
                    possible_letters = possible_letters & set(self.layer[pos].lengths[pattern.length]) # intersect
            logapp('DEBUG', 'possible most frequent letter: ' + str(possible_letters))
            possible_words = set([])
            for l in possible_letters:
                possible_words = possible_words | self._searchp_with_letters(Pattern(pattern.array_form, {most_occ:l}), 1) # union
            return possible_words

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
    def __cmp__(self, other):
        return cmp(other.has_letters(), self.has_letters()) # inverted, higher letter count figuers as smaller for pq
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
    def is_done(self):
        return self.length == self.has_letters()
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
                    elif word[i] not in testsolution.values() and word[i] not in self.solution.values():
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
    print('reading big file..')
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
        self.t = Trie(dictionary)
        self.inputfn = inputfn
        self.patterns = []
        self.hints = {}
        self.solution = {}  #dict(zip(map(lambda x: str(x), range(1,len(alphabet)+1)),map(lambda x: str(x), range(1,len(alphabet)+1)) ))
                            # {'1':'1', '2':'2', ...} to become {'1': 'a', '2': 'b', ...}
    def _is_vowel(self, letter):
        return letter in 'aeiou'

    def parse_input(self, filename="test-input.txt" ):
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
        for i in range(m):
            word = []
            for j in range(n):
                word.append(square[i][j]) if square[i][j] != '_' else None
                if square[i][j] == '_' or j == n-1:
                    patterns.append(word) if len(word) > 1 else None
                    word = []
        # vertical
        for j in range(n):
            word = []
            for i in range(m):
                word.append(square[i][j]) if square[i][j] != '_' else None
                if square[i][j] == '_' or i == m-1:
                    patterns.append(word) if len(word) > 1 else None
                    word = []
        return patterns

    def _create_patterns(self, arrays):
        for a in arrays:
            self.patterns.append(Pattern(a, self.solution))

    def _intersection(self, dict1, dict2):
        result = {}
        for k,v in dict1.items():
            if (k,v) in dict2.items():
                result[k] = v
        return result

    def check_result(self, fn):
        with open(fn, 'r') as f:
            lines = f.readlines()
            solution = dict([(l.split(',')[1].rstrip('\n'), l.split(',')[0]) for l in lines])
            for k,v in self.solution.items():
                if solution[k] != v:
                    return False
            return True

    def update_solution(self, pattern, words):
        # if there is only one word, easy
        # otherwise check if I can get at least one letter out of this to add to the solution
        if len(words) == 1:
            word = words.pop()
            for i in range(len(word)):
                self.solution[pattern.array_form[i]] = word[i]
        else:
            common = {}
            for w in words:
                testsol = pattern.check(w)
                if common == {}:
                    common = testsol
                else:
                    common = self._intersection(common, testsol)
                    if len(common) == 0:
                        return
            for k,v in common.items():
                self.solution[k] = v

    def solve(self):
        pattern_arays, self.hints = self.parse_input(self.inputfn)
        for k,v in self.hints.items():
            self.solution[k] = v
        self._create_patterns(pattern_arays)
        pq = Queue() # no priority queue, in case I get stuck with one I can't solve on top
        self.patterns.sort()
        for p in self.patterns:
            pq.put(p)
        try:
            while not pq.empty():
                p = pq.get_nowait()
                if p.is_done():
                    continue
                # try to solve, and update solution with whatever I can find
                # if it's not completely solved, put back
                self.update_solution(p, self.t.search_pattern(p))
                if p.is_done():
                    continue
                else:
                    pq.put(p)
            logapp('NOTICE', 'Solved!!!, solution is ' + str(self.solution))
        except KeyboardInterrupt:
            logapp('ERROR', 'Keyboard interrupted. still to solve:')
            while not pq.empty():
                p = pq.get_nowait()
                logapp('    ', str(p))

s = Solver(testdict, 'test-input.txt')
s.solve()