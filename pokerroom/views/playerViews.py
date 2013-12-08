__author__ = 'Todd'

import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from pokerroom.models import Player, Result


class playerPriorityList(generic.ListView):
    template_name = 'all-players.html'
    context_object_name = 'players'

    def get_queryset(self):
        return Player.objects.all()


def allPlayers(request):
    players = Player.objects.order_by('nickname')

    return HttpResponse(json.dumps([player.asDict() for player in players]), content_type="application/json")


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


def createPlayer(request):
    nickname = request.POST['nickname']

    player = Player(nickname=nickname)
    player.save()

    return redirect("/pokerroom/player")


def createPlayerForm(request):
    return render(request, 'create-player-form.html')