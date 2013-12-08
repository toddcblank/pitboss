from pokerroom.models import Player


def loggedInPlayer(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        player = Player.objects.get(user=request.user)
        return {'loggedInPlayer':player}
    else:
        # Do something for anonymous users.
        return {}