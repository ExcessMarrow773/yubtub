from django.shortcuts import render, redirect


def index(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    context = {}
    return render(request, "chat/chat.html", context)