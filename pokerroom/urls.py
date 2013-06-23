from django.conf.urls import patterns, include, url
from pokerroom import views

urlpatterns = patterns('',
    url(r'^player/create-form', views.createPlayerForm, name="createPlayerForm"),
    url(r'^player/create', views.createPlayer, name="createPlayer"),
    url(r'^player/(?P<playerId>\d+)', views.PlayerInfoView, name="playerInfo"),
    url(r'^player', views.AllPlayersView.as_view(), name="allPlayers"),
    url(r'^game/(?P<gameId>\d+)', views.viewResult, name="gameResult"),
    url(r'^game/create-form', views.createGameForm, name="createGameForm"),
    url(r'^game/create', views.createGame, name="createGame"),
    url(r'^game', views.allGames.as_view(), name="allGames"),
    url(r'^result/(?P<gameId>\d+)/add-result', views.addResult, name="addResultForm"),
)