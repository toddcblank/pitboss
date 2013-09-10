PAYOUTS = {
    2: [2],
    3: [2, 1],
    4: [3, 1],
    5: [3, 2],
    6: [3.5, 2.5],

    7: [3.5, 2, 1.5],
    8: [4, 2.5, 1.5],
    9: [4.5, 3, 1.5],
    10: [5, 3, 2],
    11: [5.5, 3.5, 2],
    12: [6.5, 3.5, 2],
    13: [6.5, 4, 2.5],

    14: [6, 4, 2.5, 1.5],
    15: [7, 4, 2.5, 1.5],
    16: [7.5, 4.5, 2.5, 1.5],
    17: [8, 4.5, 3, 1.5],
    18: [8, 5, 3, 2],
    19: [8.5, 5.5, 3, 2],
    20: [9, 5.5, 3.5, 2]
}


def getPrizeForPlace(players, place, buyin):
    print PAYOUTS
    print PAYOUTS[players]
    if place > len(PAYOUTS[players]):
        return 0

    return PAYOUTS[players][place - 1] * buyin

def getPoyPointsForPlace(numberOfPlayers, place):

    defaultPoints = 7.5
    topNinePoints = [100, 70, 50, 44, 38, 33, 28, 24, 20]


    multiplier = numberOfPlayers/9.0

    pointsForPlace = defaultPoints
    if len(topNinePoints) > place - 1:
        pointsForPlace = topNinePoints[place - 1]

    return int(pointsForPlace * multiplier)