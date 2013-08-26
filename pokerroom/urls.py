from django.conf.urls import patterns, include, url
from pokerroom import views

urlpatterns = patterns('',
    url(r'^player/create-form/?$', views.createPlayerForm, name="createPlayerForm"),
    url(r'^player/create/?$', views.createPlayer, name="createPlayer"),
    url(r'^player/(?P<playerId>\d+)/?$', views.PlayerInfoView, name="playerInfo"),
    url(r'^player/?$', views.AllPlayersView.as_view(), name="allPlayers"),

    url(r'^game/(?P<gameId>\d+)/signup-form/?$', views.gameSignup, name="gameSignup"),
    url(r'^game/(?P<gameId>\d+)/signups/?$', views.interestListJson, name="interestListJson"),
    url(r'^game/(?P<gameId>\d+)/signup/?$', views.signupPlayerForGame, name="signupPlayerForGame"),
    url(r'^game/(?P<gameId>\d+)/approve/?$', views.approvePlayerForGame, name="approvePlayerForGame"),
    url(r'^game/(?P<gameId>\d+)/signup-newplayer/?$', views.createPlayerAndSignupForGame, name="createPlayerAndSignupForGame"),
    url(r'^game/(?P<gameId>\d+)/unsignup/?$', views.unsignupPlayerForGame, name="unsignupPlayerForGame"),
    url(r'^game/(?P<gameId>\d+)/start-game?$', views.startGame, name="startGame"),
    url(r'^game/(?P<gameId>\d+)/view-game-in-progress?$', views.viewGameInProgress, name="viewGameInProgress"),
    url(r'^game/(?P<gameId>\d+)/?$', views.viewResult, name="gameResult"),



    url(r'^game/create-form/?$', views.createGameForm, name="createGameForm"),
    url(r'^game/create/?$', views.createGame, name="createGame"),
    url(r'^game/?$', views.allGames.as_view(), name="allGames"),

    url(r'^result/(?P<gameId>\d+)/add-result/?$', views.addResult, name="addResultForm"),
    url(r'^leaderboard/?$', views.leaderboard, name="leaderboards"),
    url(r'^login/?$', views.login, name="login"),
)