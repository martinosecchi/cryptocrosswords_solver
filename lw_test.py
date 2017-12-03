from lw import *

def test_pattern():
	p = Pattern(['1', '2', '4', '4', '3'], {'4':'l'})
	assert p.check('hello') is not False
	assert p.check('collo') is False
	assert p.check('a') is False
	assert p.check('12ll3') is False
	p = Pattern(['4','2','1','1','3'], {'1':'t'})
	assert p.check('tetto') is False
test_pattern()

def test_trie():
	t = Trie(testwords)
	assert t.search_word('hello')
	assert t.search_word('kjdghfnkdjbn') is False
	assert t.layer[0].children['h'].level == 1
	assert t.layer[0].children['h'].children['e'].level == 2
	assert t.layer[1].children['e'].level == 2
	assert t.layer[4].children['o'].level == 5
	assert t.search_pattern(Pattern(['1', '2', '4', '4', '3'], {'4':'l'})) == set(['hello', 'callo']) #no bollo
	assert t.search_pattern(Pattern(['1', '2', '4', '4', '3'], {'2':'e', '3':'o'})) == set(['hello', 'messo']) #no tetto
	assert t.search_pattern(Pattern(['1','2','1','1','3'], {})) == set(['tetto'])
	assert t.search_pattern(Pattern(['4','2','1','1','3'], {})) == set(['callo', 'hello', 'messo'])
test_trie()

def test_solver():
	s = Solver(testdict, 'test-input.txt')
	assert s._intersection({1:1, 2:2, 3:3}, {3:3, 4:4}) == {3:3}
	s.solve()
	assert s.check_result('test-result.txt')
	s = Solver(load_italian(), 'input.txt')
	s.solve()
	assert s.check_result('result.txt')
test_solver()