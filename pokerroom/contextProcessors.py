def loggedInPlayer(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.

        pass
    else:
        # Do something for anonymous users.
        return None