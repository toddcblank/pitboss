# Create your views here.
import json
from django.http import Http404, HttpResponse, HttpResponseServerError
from pokerroom.models import Player, Game, Result
from django.shortcuts import render, render_to_response, redirect
from django.views import generic
from datetime import date
import datetime
import operator
from django.contrib.auth import authenticate

def leaderboard(request):

    players = Player.objects.all()
    results = Result.objects.all()
    pointsPerPosition = {
        1:20, 
        2:15,
        3:12, 
        4:10, 
        5:8, 
        6:6, 
        7:4, 
        8:2, 
        9:1, 
        10:0
    }
    leaderboards = {player: 0 for player in players}
    for result in results:
        leaderboards[result.player] += pointsPerPosition[result.place]

    tuples = sorted(leaderboards.iteritems(), key=operator.itemgetter(1))
    tuples.reverse()
    model = {
        "leaderboard" : tuples
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

    interestedPlayers = Result.objects.filter(game=game, state=Result.INTERESTED)
    uninterestedPlayers = Result.objects.filter(game=game, state=Result.NOT_INTERESTED)
    unsignedupPlayers = Player.objects.all()

    model = {
        'game' : game,
        'interestedPlayers' : sorted(interestedPlayers, key=lambda result: result.player.priorityIndex, reverse=True),
        'unsignedupPlayers' : unsignedupPlayers,
        'uninterestedPlayers' : uninterestedPlayers,
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
    playerResults = Result.objects.filter(player=player)
    totalWon = sum(result.amountWon for result in playerResults)
    totalSpent = sum(result.game.buyin for result in playerResults)
    totalProfit = totalWon - totalSpent
    numberOfGames = len(playerResults)

    averageProfit = 0
    if numberOfGames > 0:
        averageProfit = totalProfit/numberOfGames

    model = {
        'player' : player,
        'results' : playerResults,
        'totalWon' : totalWon,
        'totalSpent' : totalSpent,
        'totalProfit' : totalProfit,
        'averageProfit' : averageProfit
    }

    return render(request, 'player-detail.html', model)

def signupPlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Adding interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.INTERESTED)
    


def unsignupPlayerForGame(request, gameId):
    playerId = request.POST['playerId']
    print 'Removing interest for player %s in game %s' % (playerId, gameId)
    return updatePlayerInterestInGame(playerId, gameId, Result.NOT_INTERESTED)
    


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

    return HttpResponse(json.dumps({
        'interestList' : [i.asDict() for i in interestList]
        }), content_type="application/json")


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

    return redirect("/pokerroom/game/%d/signups" % game.id)


def createPlayerForm(request):
    return render(request, 'create-player-form.html')

def createGameForm(request):
    return render(request, 'create-game-form.html')

def viewResult(request, gameId):
    game = Game.objects.filter(id=gameId)[0]
    currentResults = Result.objects.filter(game=game).order_by('place')

    model = {
        'currentResults': currentResults,
        'game': game,
    }

    return render(request, "view-result.html", model)

    pass

def addResult(request, gameId):
    game = Game.objects.filter(id=gameId)[0]

    if "playerId" in request.POST:
        playerId = request.POST['playerId']
        player = Player.objects.filter(id=playerId)[0]
        seat = request.POST['seat']
        place = request.POST['place']
        amountWon = request.POST['amountWon']

        result = Result(
            game=game,
            player=player,
            seat=seat,
            place=place,
            amountWon=amountWon
        )
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
