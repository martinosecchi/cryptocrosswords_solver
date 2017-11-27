#!/usr/bin/python
#coding: utf-8 
import json
import os, sys
import re

alphabet = [l for l in 'abcdefghijklmnopqrstuvwxyz']
testwords = list(set('hello wikipedia is a free online encyclopedia with the aim to allow anyone to edit articles wikipedia is the largest and most popular general reference work on the internet and is ranked the fifth most popular website'.split(' ')))

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
        self.layer = dict(zip(range(1, self.max_length+1), [Node() for n in range(self.max_length)]))
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
        node = self.layer[layer]
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

    def search_word(self, word):
        node = self.layer[1]
        for i in range(len(word)):
            if node.lengths.has_key(len(word)) and word[i] in node.lengths[len(word)]:
                node = node.children[word[i]]
            else:
                return False
        return word in node.words

    def search_pattern(self, pattern):
        pass

t = Trie(testwords)

def load_english(filename="words_dictionary.json"):
    with open(filename,"r") as english_dictionary:
        valid_words = json.load(english_dictionary)
        return valid_words.keys()
def load_italian(filename="../parole/parole.txt"):
    lines = []
    with open(filename, "r") as f:
        for line in f:
            try:
                word = line.decode('utf8')
                word.replace(u'à', 'a')
                word.replace(u'á', 'a')
                word.replace(u'è', 'e')
                word.replace(u'é', 'e')
                word.replace(u'í', 'i')
                word.replace(u'ì', 'i')
                word.replace(u'ò', 'o')
                word.replace(u'ó', 'o')
                word.replace(u'ù', 'u')
                word.replace(u'ú', 'u')
                for l in word:
                    if l not in alphabet + ['\n']:
                        raise Exception(l.decode('utf8') + u' - not in alphabet')
                lines.append(word.rstrip('\n').encode('utf8'))
            except Exception as e:
                print 'unicode error: ' + line.rstrip('\n'), str(e)
    return lines

# it = load_italian()

def validate(lines, n, m):
    pattern = re.compile(r'[_]{1}|[0-9]{1,2}')
    try:
        assert len(lines) == m
        for l in lines:
            assert len(l) == n
            for e in range(len(l)):
                l[e] = l[e].rstrip('\n')
                assert pattern.match(l[e]) is not None
    except AssertionError as ae:
        print 'Error in input: validate failed.', ae

def parse_input():
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
    validate(lines, n, m)
    return lines, hints

square, hints = parse_input()

def flatten(square, n, m):
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
