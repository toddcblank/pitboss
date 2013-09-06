PAYOUTS = {
2:[2],
3:[2,1],
4:[3,1],
5:[3.5,1.5],
6:[4,2],
7:[4,2,1],
8:[4,2.5,1.5],
9:[5,2.5,1.5],
10:[5,3,2],
11:[6,3,2],
}

def getPrizeForPlace(players, place, buyin):
	return PAYOUTS[players][place] * buyin
