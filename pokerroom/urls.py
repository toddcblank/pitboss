from django.conf.urls import patterns, include, url
from pokerroom.views import gameViews, leaderboardViews, loginViews, playerViews

urlpatterns = patterns('',
    url(r'^player/create-form/?$', playerViews.createPlayerForm, name="createPlayerForm"),
    url(r'^player/create/?$', playerViews.createPlayer, name="createPlayer"),
    url(r'^player/(?P<playerId>\d+)/?$', playerViews.PlayerInfoView, name="playerInfo"),
    url(r'^player/?$', playerViews.AllPlayersView.as_view(), name="allPlayers"),

    url(r'^game/(?P<gameId>\d+)/signup-form/?$', gameViews.gameSignup, name="gameSignup"),
    url(r'^game/(?P<gameId>\d+)/signups/?$', gameViews.interestListJson, name="interestListJson"),
    url(r'^game/(?P<gameId>\d+)/signup/?$', gameViews.signupPlayerForGame, name="signupPlayerForGame"),
    url(r'^game/(?P<gameId>\d+)/approve/?$', gameViews.approvePlayerForGame, name="approvePlayerForGame"),
    url(r'^game/(?P<gameId>\d+)/signup-newplayer/?$', gameViews.createPlayerAndSignupForGame, name="createPlayerAndSignupForGame"),
    url(r'^game/(?P<gameId>\d+)/unsignup/?$', gameViews.unsignupPlayerForGame, name="unsignupPlayerForGame"),
    url(r'^game/(?P<gameId>\d+)/start-game?$', gameViews.startGame, name="startGame"),
    url(r'^game/(?P<gameId>\d+)/unstart-game?$', gameViews.unstartGame, name="unstartGame"),

    url(r'^game/(?P<gameId>\d+)/remove-player?$', gameViews.removePlayerFromGameInProgress, name="removePlayerFromGameInProgress"),
    url(r'^game/(?P<gameId>\d+)/view-game-in-progress?$', gameViews.viewGameInProgress, name="viewGameInProgress"),
    url(r'^game/(?P<gameId>\d+)/?$', gameViews.viewResult, name="gameResult"),
    url(r'^game/create-form/?$', gameViews.createGameForm, name="createGameForm"),
    url(r'^game/create/?$', gameViews.createGame, name="createGame"),

    url(r'^game/(?P<gameId>\d+)/game-view/?$', gameViews.gameViewEndpoint, name="gameView"),
    url(r'^game/(?P<gameId>\d+)/seat-player/?$', gameViews.seatPlayerPost, name="gameView"),
    url(r'^game/(?P<gameId>\d+)/eliminate-player?$', gameViews.elminatePlayerPost, name="eliminatePlayer"),
    url(r'^game/(?P<gameId>\d+)/undo-eliminate-player?$', gameViews.undoElminatePlayerPost, name="undoElminatePlayer"),
    url(r'^game/(?P<gameId>\d+)/unseat-player?$', gameViews.unseatPlayerPost, name="unseatPlayerPost"),
    url(r'^game/(?P<gameId>\d+)/balance-tables?$', gameViews.balanceTablesPost, name="balanceTablesPost"),
    url(r'^game/(?P<gameId>\d+)/reseat-players?$', gameViews.reseatPlayersPost, name="reseatPlayersPost"),
    url(r'^game/(?P<gameId>\d+)/player-interested?$', gameViews.playerInterestedPost, name="playerInterestedPost"),
    url(r'^game/?$', gameViews.allGames.as_view(), name="allGames"),



    url(r'^result/(?P<gameId>\d+)/add-result/?$', gameViews.addResult, name="addResultForm"),

    url(r'^leaderboard/?$', leaderboardViews.leaderboard, name="leaderboards"),
    url(r'^leaderboard-pergame/?$', leaderboardViews.moneyPerGameLeaderboard, name="moneyPerGameLeaderboard"),
    url(r'^poy-leaderboard/?$', leaderboardViews.pointsLeaderboard, name="pointsLeaderboard"),

    url(r'^login/?$', loginViews.loginPage, name="login"),
)
