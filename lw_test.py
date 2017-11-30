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
	assert t.layer[0].children['h'].level == 1
	assert t.layer[0].children['h'].children['e'].level == 2
	assert t.layer[1].children['e'].level == 2
	assert t.layer[4].children['o'].level == 5
	assert t.search_pattern(Pattern(['1', '2', '4', '4', '3'], {'4':'l'}))
	assert t.search_pattern(Pattern(['1', '2', '4', '4', '3'], {'2':'e', '3':'o'}))
test_trie()
