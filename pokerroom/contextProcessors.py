from pokerroom.models import Player


def loggedInPlayer(request):

    try:
        if request.user.is_authenticated():
            # Do something for authenticated users.
            player = Player.objects.get(user=request.user)
            return {'loggedInPlayer':player}
    except:
        pass

    return {}