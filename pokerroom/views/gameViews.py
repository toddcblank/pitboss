from django.contrib.auth.decorators import login_required

__author__ = 'Todd'

# Create views related to games here.
import json
import random
import math
from django.http import HttpResponse
from pokerroom.models import Player, Game, Result
from django.shortcuts import render, redirect
from django.views import generic
from datetime import date
from django.db.models import Q
from pokerroom import payouts
from random import choice


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
        'sortedInterestList': sortedInterestList
    }

    return render(request, 'signup.html', model)


def allPlayers(request):
    players = Player.objects.order_by('nickname')

    return HttpResponse(json.dumps([player.asDict() for player in players]), content_type="application/json")


class allGames(generic.ListView):
    template_name = 'all-games.html'
    context_object_name = 'games'

    def get_queryset(self):
        return Game.objects.all()


class AllPlayersView(generic.ListView):
    template_name = 'all-players.html'
    context_object_name = 'players'

    def get_queryset(self):
        return sorted(Player.objects.all(), key=lambda x: x.nickname)


def PlayerInfoView(request, playerId):
    player = Player.objects.get(id=playerId)
    playerResults = Result.objects.filter(player=player, state=Result.FINISHED)
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
    return updatePlayerInterestInGame(playerId, gameId, Result.NOT_SPECIFIED)

def removePlayerFromGameInProgress(request, gameId):
    playerId = request.POST['playerId']
    print 'Removing player %s from in progress game %s' % (playerId, gameId)

    updatePlayerInterestInGame(playerId, gameId, Result.NOT_SPECIFIED)

    #We need to update everyone who has been eliminated to move up one spot
    game = Game.objects.get(id=gameId)
    existingFinishedResults = Result.objects.filter(game=game, state=Result.FINISHED)
    for result in existingFinishedResults:
        result.place = result.place - 1
        result.save()

    return redirect("/pokerroom/game/%d/view-game-in-progress" % game.id)

#NYI - would be nice to be able to just add people as a game has started.  Need to think of a good way to do this.
def addPlayerToGameInProgress(request, gameId):
    return redirect("/pokerroom/game/%d/view-game-in-progress" % game.id)


def updatePlayerInterestInGame(playerId, gameId, newState):
    player = Player.objects.get(id=playerId)
    game = Game.objects.get(id=gameId)
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
    return redirect("/pokerroom/game/%d/game-view" % game.id)

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
    if len(results) == 0:
        return redirect("/pokerroom/game/%d/signup-form" % game.id)

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

def interestListJson(request, gameId):
    game = Game.objects.get(id=gameId)

    interestList = Result.objects.filter(game=game)
    sortedInterestList = sorted(interestList, key=lambda result: (result.state, result.player.priorityIndex),
                                reverse=True)

    return HttpResponse(json.dumps({
        'interestList': [i.asDict() for i in sortedInterestList]
    }), content_type="application/json")

# @login_required(login_url='/pokerroom/login')
def signupPlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Adding interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.INTERESTED)

# @login_required(login_url='/pokerroom/login')
def approvePlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Adding interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.PLAYING)

# @login_required(login_url='/pokerroom/login')
def unsignupPlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Removing interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.NOT_SPECIFIED)

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


class allGames(generic.ListView):
    template_name = 'all-games.html'
    context_object_name = 'games'

    def get_queryset(self):
        return sorted(Game.objects.all(), key=lambda x: x.datePlayed, reverse=True)


# @login_required(login_url='/pokerroom/login')
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


### Everything above is old, and possibly deprecated, and needs to be cleaned up
def getRandomOpenSeatForTable(game, table):
    activePlayers = Result.objects.filter(game=game, state=Result.PLAYING, table=table)
    seatsPerTable = 10
    allSeats = range(0, seatsPerTable)
    for activePlayer in activePlayers:
        allSeats.remove(activePlayer.seat - 1)

    return choice(allSeats) + 1

#finds an open seat in a game
def getRandomOpenSeat(game):

    activePlayers = Result.objects.filter(game=game, state=Result.PLAYING)

    #these could fluctuate if we get a lot of players
    seatsPerTable = 10
    numTables = 2
    allSeats = range(0, seatsPerTable * numTables)

    for activePlayer in activePlayers:
        allSeats.remove((activePlayer.table - 1) * seatsPerTable + (activePlayer.seat - 1))

    seat = choice(allSeats)
    seatValue = (seat % seatsPerTable) + 1
    tableValue = math.floor(float(seat)/seatsPerTable) + 1

    return tableValue, seatValue


# Seats a player in the game.  This will random them to a seat on one of two tables
# it will NOT keep the tables balanced

#### Endpoints ###
def gameViewEndpoint(request, gameId):
    game = Game.objects.get(id=gameId)

    playersInGame = Result.objects.filter(game=game, state=Result.PLAYING)
    finishedPlayers = Result.objects.filter(game=game, state=Result.FINISHED)
    interestedPlayers = [r.player for r in Result.objects.filter(game=game, state=Result.INTERESTED)]
    otherPlayers = [r.player for r in Result.objects.filter(game=game, state=Result.NOT_SPECIFIED)]

    model = {
        'gamePlayerList': sorted(playersInGame, key=lambda x: x.seat + x.table * 100),
        'finishedPlayers': sorted(finishedPlayers, key=lambda x: x.place),
        'interestList': sorted(interestedPlayers, key=lambda x: x.nickname),
        'otherPlayers': sorted(otherPlayers, key=lambda x: x.nickname),
        'game': game,
        'payouts': [payout * game.buyin for payout in payouts.PAYOUTS[len(playersInGame) + len(finishedPlayers)]]
    }

    return render(request, 'game-view.html', model)

def seatPlayerPost(request, gameId):
    if 'playerId' in request.POST:
        seatPlayerInGame(gameId, request.POST['playerId'])

    return redirect("/pokerroom/game/%s/game-view" % gameId)

def elminatePlayerPost(request, gameId):
    if 'playerId' in request.POST:
        elminatePlayer(gameId, request.POST['playerId'])

    return redirect("/pokerroom/game/%s/game-view" % gameId)

def undoElminatePlayerPost(request, gameId):
    if 'playerId' in request.POST:
        undoElminatePlayer(gameId, request.POST['playerId'])

    return redirect("/pokerroom/game/%s/game-view" % gameId)

def unseatPlayerPost(request, gameId):
    if 'playerId' in request.POST:
        unseatPlayer(gameId, request.POST['playerId'])

    return redirect("/pokerroom/game/%s/game-view" % gameId)

def balanceTablesPost(request, gameId):
    balanceTables(gameId, 1, 10)
    return redirect("/pokerroom/game/%s/game-view" % gameId)

def playerInterestedPost(request, gameId):
    game = Game.objects.get(id=gameId)
    if 'playerId' in request.POST:
        player = Player.objects.get(id=request.POST['playerId'])
        playerResult = Result.objects.filter(game=game, player=player)[0]
        playerResult.state = Result.INTERESTED
        playerResult.save()
    return redirect("/pokerroom/game/%s/game-view" % gameId)
### Common Methods ###
def seatPlayerInGame(gameId, playerId):
    game = Game.objects.get(id=gameId)
    player = Player.objects.get(id=playerId)

    result = Result.objects.filter(game=game, player=player)[0]
    result.state = Result.PLAYING

    table, seat = getRandomOpenSeat(game)

    if player.priority == Player.FACILITATOR:
        dealerPresent = Result.objects.filter(game=game, table=1, seat=1, state=Result.PLAYING)
        
        #put facilitators in dealer seat if there's no one there.
        if not dealerPresent:
            table = 1
            seat = 1

    result.table = table
    result.seat = seat

    result.save()

    #check if we have any finished players, if we do we need to bump them down
    eliminatedPlayers = Result.objects.filter(game=game, state=Result.FINISHED)
    for eliminatedPlayer in eliminatedPlayers:
        eliminatedPlayer.place = eliminatedPlayer.place + 1
        eliminatedPlayer.save()

#Unseats a player, in case we seated the wrong one.
def unseatPlayer(gameId, playerId):
    game = Game.objects.get(id=gameId)
    player = Player.objects.get(id=playerId)

    result = Result.objects.filter(game=game, player=player)[0]
    result.state = Result.INTERESTED
    result.table = None
    result.seat = None
    result.save()

    #check if we have any finished players, if we do we need to bump them up
    eliminatedPlayers = Result.objects.filter(game=game, state=Result.FINISHED)
    for eliminatedPlayer in eliminatedPlayers:
        eliminatedPlayer.place = eliminatedPlayer.place - 1
        eliminatedPlayer.save()

def breakTable(game, table):
    print "Breaking up table %d" % table
    playersToMove = Result.objects.filter(game=game, state=Result.PLAYING, table=table)

    for player in playersToMove:
        #get the table with the fewest players
        seatedPlayers = Result.objects.filter(game=game, state=Result.PLAYING).exclude(table=table)

        playercounts = [0] * (table - 1)
        for activePlayer in seatedPlayers:

            playercounts[activePlayer.table - 1] += 1

        newTable = playercounts.index(min(playercounts)) + 1
        #move player to that table
        newSeat = getRandomOpenSeatForTable(game, newTable)

        print "Moving %s from %d-%d to %d-%d" % (player.player, player.table, player.seat, newTable, newSeat)
        player.table = newTable
        player.seat = newSeat
        player.save()

#balances tables, distributing players in game to some number of tables
#will move players from the most populated to the least populated
def balanceTables(gameId, minimumNumberOfTables, maxPlayersPerTable):
    game = Game.objects.get(id=gameId)
    activePlayers = Result.objects.filter(game=game, state=Result.PLAYING)

    currentTables = max(r.table for r in activePlayers)
    print "current number of tables: %d" % currentTables

    numberOfTables = minimumNumberOfTables
    while len(activePlayers) > numberOfTables * maxPlayersPerTable:
        numberOfTables += 1

    if currentTables > numberOfTables:
        return breakTable(game, currentTables)

    minPlayersPerTable = math.ceil(len(activePlayers)/numberOfTables)

    playercounts = [0] * numberOfTables
    for activePlayer in activePlayers:
        playercounts[activePlayer.table - 1] += 1

    print "Current table counts: "
    print playercounts

    # check if we're balanced already
    if (min(playercounts) >= minPlayersPerTable):
        print "tables are balanced.  not moving anyone"
        return

    # nope.
    # move one from the most populated table
    overloadedTable = playercounts.index(max(playercounts)) + 1
    mover = choice(Result.objects.filter(game=game, state=Result.PLAYING, table=overloadedTable))

    #get a new empty seat from the other table
    newTable = playercounts.index(min(playercounts)) + 1;
    newSeat = getRandomOpenSeatForTable(game, newTable)

    print "Moving %s from %d-%d to %d-%d" % (mover.player, mover.table, mover.seat, newTable, newSeat)
    mover.seat = newSeat
    mover.table = newTable
    mover.save()

#reseats a single specific player.  could be handy
def reseatSinglePlayer(gameId, playerId):

    game = Game.objects.get(id=gameId)
    player = Player.objects.get(id=playerId)

    result = Result.objects.filter(game=game, player=player)[0]
    result.state = Result.PLAYING

    table, seat = getRandomOpenSeat(game)
    result.table = table
    result.seat = seat

    result.save()

# locks game down.  prevents new players from registering.  reseating will now reduce down to 1 table if possible
def lockGame(gameId):
    setGameState(gameId, Game.STARTED_LOCKED)

def startGame(gameId):
    setGameState(gameId, Game.STARTED)

def setGameState(gameId, newState):
    game = Game.objects.get(id=gameId)
    game.gameState = newState
    game.save()

# eliminates the player from the game
def elminatePlayer(gameId, playerId):
    game = Game.objects.get(id=gameId)
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

# un-does player elimination in case of mistake.  will place them in their old seat.
# if people have been reseated we may have problems.
def undoElminatePlayer(gameId, playerId):
    game = Game.objects.get(id=gameId)
    player = Player.objects.get(id=playerId)

    result = Result.objects.filter(game=game, player=player)[0]

    result.place = None
    result.amountWon = 0

    result.state = Result.PLAYING
    result.save()
    print "un-Eliminating %s" % (player.nickname)
