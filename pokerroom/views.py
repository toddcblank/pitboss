# Create your views here.
import json
import random
from django.http import Http404, HttpResponse, HttpResponseServerError
from pokerroom.models import Player, Game, Result
from django.shortcuts import render, render_to_response, redirect
from django.views import generic
from datetime import date
from django.db.models import Q
import operator
from django.contrib.auth import authenticate
import payouts


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


def login(request):
    if request.method == "POST":
        name = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=name, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return redirect('/pokerroom/game')

    return render(request, 'login.html')


class playerPriorityList(generic.ListView):
    template_name = 'all-players.html'
    context_object_name = 'players'

    def get_queryset(self):
        return Player.objects.all()


def gameSignup(request, gameId):
    game = Game.objects.get(id=gameId)

    interestList = Result.objects.filter(game=game)
    sortedInterestList = sorted(
        interestList,
        key=lambda result: (result.state * -1, int(result.player.priorityIndex))
    )


    model = {
        'game': game,
        'sortedInterestList': sortedInterestList,
    }

    return render(request, 'signup.html', model)


def allPlayers(request):
    players = Player.objects.order_by('nickname')

    return HttpResponse(json.dumps([player.asDict() for player in players]), content_type="application/json")


class allGames(generic.ListView):
    template_name = 'all-games.html'
    context_object_name = 'games'

    def get_queryset(self):
        return sorted(Game.objects.all(), key=lambda x: x.datePlayed, reverse=True)


class AllPlayersView(generic.ListView):
    template_name = 'all-players.html'
    context_object_name = 'players'

    def get_queryset(self):
        return sorted(Player.objects.all(), key=lambda x: x.nickname)


def PlayerInfoView(request, playerId):
    player = Player.objects.get(id=playerId)
    playerResults = sorted(Result.objects.filter(player=player, state=Result.FINISHED), key=lambda x: x.game.datePlayed, reverse=True) 
    totalWon = sum(result.amountWon for result in playerResults)
    totalSpent = sum(result.game.buyin for result in playerResults)
    totalProfit = totalWon - totalSpent
    numberOfGames = len(playerResults)

    averageProfit = 0
    if numberOfGames > 0:
        averageProfit = totalProfit / numberOfGames

    model = {
        'player': player,
        'results': playerResults,
        'totalWon': totalWon,
        'totalSpent': totalSpent,
        'totalProfit': totalProfit,
        'averageProfit': averageProfit
    }

    return render(request, 'player-detail.html', model)


def signupPlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Adding interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.INTERESTED)


def approvePlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Adding interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.PLAYING)


def unsignupPlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Removing interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.INTERESTED)


def updatePlayerInterestInGame(playerId, gameId, newState):
    player = Player.objects.get(id=playerId)
    game = Game.objects.get(id=gameId)
    #try:
    existingResults = Result.objects.filter(game=game, player=player)

    if len(existingResults) >= 1:
        existingResult = existingResults[0]
        print 'Found existing result for player %d for gameId %d' % (player.id, game.id)
        existingResult.state = newState
        existingResult.save()
    else:
        result = Result(
            game=game,
            player=player,
            state=newState
        )
        print 'Creating new result for game %d player %d state %d' % (game.id, player.id, newState)
        result.save()

    return HttpResponse(json.dumps({}), content_type="application/json")


def interestListJson(request, gameId):
    game = Game.objects.get(id=gameId)

    interestList = Result.objects.filter(game=game)
    sortedInterestList = sorted(
        interestList,
        key=lambda result: (result.state * -1, int(result.player.priorityIndex))
    )

    return HttpResponse(json.dumps({
        'interestList': [i.asDict() for i in sortedInterestList]
    }), content_type="application/json")


def createPlayerAndSignupForGame(request, gameId):
    nickname = request.POST['nickname']
    existingUser = Player.objects.filter(nickname=nickname)
    game = Game.objects.get(id=gameId)

    player = None
    if len(existingUser) == 0:
        print "Found no users with nickname %s " % nickname
        player = Player(nickname=nickname)
        player.save()

    else:
        print "Found existing user with nickname %s " % nickname
        player = existingUser[0]

    existingSignup = Result.objects.filter(game=game, player=player)
    result = None
    if len(existingSignup) == 0:
        result = Result(
            game=game,
            player=player,
            state=Result.INTERESTED
        )
    else:
        result = existingSignup[0]
        result.state = Result.INTERESTED

    result.save()

    return HttpResponse(json.dumps({"success": True}), content_type="application/json")


def createPlayer(request):
    nickname = request.POST['nickname']

    player = Player(nickname=nickname)
    player.save()

    return redirect("/pokerroom/player")


def createGame(request):
    buyin = float(request.POST['buyin'])
    datePlayed = request.POST['datePlayed']
    day = int(datePlayed.split('/')[1])
    month = int(datePlayed.split('/')[0])
    year = int(datePlayed.split('/')[2])

    game = Game(buyin=buyin, gameType=Game.NL_TEXAS_HOLDEM, datePlayed=date(year, month, day))
    game.save()

    playerList = Player.objects.all()
    for player in playerList:
        result = Result(
            game=game,
            player=player)
        result.save()
    return redirect("/pokerroom/game/%d/signup-form" % game.id)


def createPlayerForm(request):
    return render(request, 'create-player-form.html')


def createGameForm(request):
    return render(request, 'create-game-form.html')


def viewResult(request, gameId):
    game = Game.objects.get(id=gameId)
    currentResults = Result.objects.filter(game=game, state=Result.FINISHED).order_by('place')

    model = {
        'currentResults': currentResults,
        'game': game,
    }

    return render(request, "view-result.html", model)


def viewGameInProgress(request, gameId):
    game = Game.objects.get(id=gameId)

    results = Result.objects.filter(Q(game=game, state=Result.PLAYING) | Q(game=game, state=Result.FINISHED))

    model = {
        "game": game,
        "playerList": sorted(results, key=lambda x: x.seat),
        "payouts": [payout * game.buyin for payout in payouts.PAYOUTS[len(results)]]
    }
    return render(request, "view-game-in-progress.html", model)


"""
   Starts game with the current players that are approved.  should prevent further approving/signup

   Will assign seats to everyone in the following order:
       1. if Todd is playing he gets seat 1.
       2. first found non-Todd facilitator gets seat 1
       3. Randomize the rest
"""


def startGame(request, gameId):
    game = Game.objects.get(id=gameId)

    results = Result.objects.filter(game=game, state=Result.PLAYING)

    dealerFound = False

    for result in results:
        if result.player.nickname == "Todd Blank":
            result.seat = 1
            result.save()
            dealerFound = True
            break

    seatList = range(2, len(results) + 1)
    random.shuffle(seatList)
    seatIndex = 0
    print "seatIndexs:"
    print seatList

    for result in results:
        if result.player.nickname == "Todd Blank":
            pass
        elif (result.player.priority == result.player.HIGH or result.player.priority == result.player.FACILITATOR) and not dealerFound:
            result.seat = 1
            result.save()
            dealerFound = True
        else:
            print "placing %s in seatIndex %d " % (result.player, seatIndex)
            result.seat = seatList[seatIndex]
            result.save()
            seatIndex += 1

    return redirect("/pokerroom/game/%d/view-game-in-progress" % game.id)


# Unseats everyone, essentially unstarting the game.
def unstartGame(request, gameId):
    game = Game.objects.get(id=gameId)

    results = Result.objects.filter(game=game, state=Result.PLAYING)
    for result in results:
        result.seat = None
        result.save()

    model = {
        "playerList": results
    }
    return redirect("/pokerroom/game/%d/signup-form" % game.id)


def elminatePlayer(request, gameId):
    game = Game.objects.get(id=gameId)

    playerId = request.POST['playerId']
    player = Player.objects.get(id=playerId)

    result = Result.objects.filter(game=game, player=player)[0]

    playersStillActive = Result.objects.filter(game=game, state=Result.PLAYING)
    eliminatedResults = Result.objects.filter(game=game, state=Result.FINISHED).order_by('place')

    result.place = len(playersStillActive)
    result.amountWon = payouts.getPrizeForPlace(
        len(playersStillActive) + len(eliminatedResults),
        result.place,
        game.buyin
    )

    result.state = Result.FINISHED
    result.save()
    print "Eliminating %s in %s place" % (player.nickname, result.placeAsOrdinal)

    return redirect("/pokerroom/game/%d/view-game-in-progress" % game.id)


def undoElminatePlayer(request, gameId):
    game = Game.objects.get(id=gameId)

    playerId = request.POST['playerId']
    player = Player.objects.get(id=playerId)

    result = Result.objects.filter(game=game, player=player)[0]

    result.place = None
    result.amountWon = 0

    result.state = Result.PLAYING
    result.save()
    print "un-Eliminating %s" % (player.nickname)

    return redirect("/pokerroom/game/%d/view-game-in-progress" % game.id)


def addResult(request, gameId):
    game = Game.objects.get(id=gameId)

    if "playerId" in request.POST:
        playerId = request.POST['playerId']
        player = Player.objects.filter(id=playerId)[0]
        place = request.POST['place']
        amountWon = request.POST['amountWon']

    result = Result.objects.filter(game=game, player=player)[0]

    result.place = place
    result.amountWon = amountWon
    result.save()

    players = Player.objects.all()

    currentResults = Result.objects.filter(game=game).order_by('place')
    nextPlace = 0
    if len(currentResults) > 0:
        nextPlace = currentResults[0].place - 1
    eliminatedPlayers = [result.player.id for result in currentResults]

    model = {
        'players': sorted(players, key=lambda x: x.nickname),
        'currentResults': currentResults,
        'nextPlace': nextPlace,
        'game': game,
        'eliminatedPlayers': eliminatedPlayers
    }

    return render(request, "add-result.html", model)
