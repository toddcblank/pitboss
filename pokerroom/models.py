from django.db import models
from django.contrib.auth.models import User
import hashlib

# Create your models here.
class Player(models.Model):

    FACILITATOR = 100
    HIGH = 50
    NORMAL = 20
    LOW = 10
    NONE = 0

    PRIORITY_TYPES = [
        (FACILITATOR, "Top Priority (Facilitator)"),
        (HIGH, "High"),
        (NORMAL, "Normal"),
        (LOW, "Low"),
        (NONE, "Lowest"),
    ]

    nickname = models.CharField(max_length=128)
    user = models.OneToOneField(User, blank=True, null=True)
    priority = models.IntegerField(default=NORMAL, choices=PRIORITY_TYPES)


    @property
    def username(self):
        try:
            if self.user and self.user is not None:
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

    @property
    def priorityIndex(self):
        lastResults = Result.objects.filter(player=self, state=Result.FINISHED).order_by('game')

        datePart = '99999999'
        placePart = '999'

        if len(lastResults) > 0:
            lastResult = lastResults[0]
            datePart = str(lastResult.game.datePlayed.year) + str(lastResult.game.datePlayed.month).zfill(2) + str(lastResult.game.datePlayed.day).zfill(2)
            placePart = str(lastResult.place).zfill(2)

        return str(self.priority).zfill(3) + datePart + placePart

    def asDict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "priorityIndex": self.priorityIndex
        }

    def __str__(self):
        if self.user and self.user.get_full_name():
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
        return "(%d) %s on %s" % (self.id, self.get_gameType_display(), self.datePlayed.__str__())

    @property
    def desc(self):
        return "(%d) %s on %s" % (self.id, self.get_gameType_display(), self.datePlayed.__str__())

class Result(models.Model):

    FINISHED = 3
    PLAYING = 2
    INTERESTED = 1
    NOT_SPECIFIED = 0
    NOT_INTERESTED = -1

    RESULT_STATE = [
        (FINISHED, "Finished"),
        (PLAYING, "Playing"),
        (INTERESTED, "Interested"),
        (NOT_SPECIFIED, "Not Specified"),
        (NOT_INTERESTED, "Not Interested")
    ]

    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    seat = models.IntegerField(blank=True, null=True)
    place = models.IntegerField(blank=True, null=True)
    amountWon = models.FloatField(default=0)
    state = models.IntegerField(default=NOT_SPECIFIED, choices=RESULT_STATE)

    suffixes = ["th", "st", "nd", "rd", ] + ["th"] * 16


    def asDict(self):
        return {
            "id": self.id,
            "gameId": self.game.id,
            "player": self.player.asDict(),
            "place": self.place,
            "amount": self.amountWon,
            "seat": self.seat,
            "state": self.get_state_display(),
        }

    @property
    def profit(self):
        if self.amountWon:
            return self.amountWon - self.game.buyin
        return 0 - self.game.buyin

    @property
    def placeAsOrdinal(self):
        if self.place > 0:
            return str(self.place) + self.suffixes[self.place % 100]
        else:
            return ""

    def __str__(self):
        if self.amountWon:
            return "%s placed %d and won %d in game %d" % (self.player, self.place, self.amountWon, self.game.id)
        return "%s is %s in game %d" % (self.player, self.get_state_display(), self.game.id)