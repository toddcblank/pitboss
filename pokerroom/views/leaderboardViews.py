__author__ = 'Todd'

import operator

from django.shortcuts import render

from pokerroom.models import Player, Result


def pointsLeaderboard(request):
    players = Player.objects.all()
    leaderboards = {player: 0 for player in players}

    for player in players:
        playerResults = Result.objects.filter(state=Result.FINISHED, player=player)
        leaderboards[player] = sum([result.poyPoints for result in playerResults])

    tuples = sorted(leaderboards.iteritems(), key=operator.itemgetter(1))
    tuples.reverse()
    model = {
        "leaderboard": tuples
    }

    return render(request, 'leaderboard.html', model)


def moneyPerGameLeaderboard(request):
    players = Player.objects.all()
    leaderboards = {player: 0 for player in players}

    for player in players:
        playerResults = Result.objects.filter(state=Result.FINISHED, player=player)
        if len(playerResults) > 0:
            leaderboards[player] = sum([result.profit for result in playerResults]) / len(playerResults)

    tuples = sorted(leaderboards.iteritems(), key=operator.itemgetter(1))
    tuples.reverse()
    model = {
        "leaderboard": tuples
    }

    return render(request, 'leaderboard.html', model)


def leaderboard(request):
    players = Player.objects.all()
    results = Result.objects.filter(state=Result.FINISHED)
    leaderboards = {player: 0 for player in players}
    for result in results:
        leaderboards[result.player] += result.profit

    tuples = sorted(leaderboards.iteritems(), key=operator.itemgetter(1))
    tuples.reverse()
    model = {
        "leaderboardDescription": "Total Profit",
        "leaderboard": tuples
    }

    return render(request, 'leaderboard.html', model)
