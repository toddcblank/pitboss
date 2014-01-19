from pokerroom.models import Player
from django.conf import settings

def loggedInPlayer(request):

    try:
        if request.user.is_authenticated():
            # Do something for authenticated users.
            player = Player.objects.get(user=request.user)
            return {'loggedInPlayer':player}
    except:
        pass

    return {}

def appLocation(request):
    return {'appLocation':settings.PITBOSS_APP_LOCATION}