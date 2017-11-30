from lw import *

def test_pattern():
	p = Pattern(['1', '2', '4', '4', '3'], {'4':'l'})
	assert p.check('hello') is not False
	assert p.check('collo') is False
	assert p.check('a') is False
	assert p.check('12ll3') is False
test_pattern()

def test_trie():
	t = Trie(testwords)
	assert t.search_word('hello')
	assert t.search_word('kjdghfnkdjbn') is False
test_trie()
