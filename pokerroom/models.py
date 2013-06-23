from django.db import models
import hashlib

# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=64)
    nickname = models.CharField(max_length=128)
    email = models.CharField(max_length=1024)


    @property
    def gravatarId(self):
        #this is kind of wasteful to recalculate every request.  but meh.
        md = hashlib.md5()
        md.update(self.email.strip().lower())
        return md.hexdigest()

    def asDict(self):
        return {
            "id": self.id,
            "name": self.name,
            "nickname": self.nickname,
            "email": self.email
        }

    def __str__(self):
        return self.name


class Game(models.Model):
    NL_TEXAS_HOLDEM = 0

    GAME_TYPES = [
        (NL_TEXAS_HOLDEM, "NL Texas Hold'em Tournament")
    ]

    buyin = models.FloatField()
    gameType = models.IntegerField(default=0, choices=GAME_TYPES)
    datePlayed = models.DateTimeField()

    def asDict(self):
        return {
            "id": self.id,
            "buyin": self.buyin,
            "gameType": self.get_gameType_display(),
            "datePlayed": self.datePlayed.__str__()
        }

    def __str__(self):
        return self.get_gameType_display() + " on " + self.datePlayed.__str__()

    @property
    def desc(self):
        return "burglefrickle"

class Result(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    seat = models.IntegerField()
    place = models.IntegerField()
    amountWon = models.FloatField()

    def asDict(self):
        return {
            "id": self.id,
            "gameId": self.game.id,
            "player": self.player.asDict(),
            "place": self.place,
            "amount": self.amountWon,
            "seat": self.seat
        }

    @property
    def profit(self):
        return self.amountWon - self.game.buyin

    def __str__(self):
        return "%s placed %d and won %d in game %d" % (self.player, self.place, self.amountWon, self.game.id)