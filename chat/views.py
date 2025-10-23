from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from app.models import User

# Create your views here.
User = get_user_model()

def index(request):
    user = get_object_or_404(User, username=request.user.username)
    following = user.following.all()

    following_names = []
    for i in following:
        following_names.append(i.username)

    friends = []
    for i in following:
        if user in i.following.all():
            friends.append(i)

    context = {
        "friends": friends
    }
    return render(request, 'chatIndex.html', context)

def chat(request, account):
    user = get_object_or_404(User, username=account)
    context = {
        'account': user
    }

    return render(request, 'chat.html', context)