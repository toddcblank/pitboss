__author__ = 'Todd'

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def loginPage(request):
    if request.method == "POST":
        name = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=name, password=password)
        if user is not None and user.is_active:
            login(request, user)

            return redirect('/pokerroom/game')

    return render(request, 'login.html')