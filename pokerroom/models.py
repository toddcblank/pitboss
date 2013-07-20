from django.db import models
from django.contrib.auth.models import User
import hashlib

# Create your models here.
class Player(models.Model):

    nickname = models.CharField(max_length=128)
    user = models.OneToOneField(User, blank=True)

    @property
    def username(self):
        try:
            if self.user:
                return self.user.get_full_name()
            else:
                return self.nickname
        except:
            return self.nickname

    @property
    def gravatarId(self):
        #this is kind of wasteful to recalculate every request.  but meh.
        md = hashlib.md5()
        md.update(self.user.email.strip().lower())
        return md.hexdigest()

    def asDict(self):
        return {
            "id": self.id,
            "name": self.name(),
            "nickname": self.nickname,
            "email": self.user.email
        }

    def __str__(self):
        if self.user.get_full_name():
            return self.user.get_full_name()

        return self.nickname


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