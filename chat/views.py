from django.shortcuts import render
from django.contrib.auth import get_user_model
# Create your views here.
User = get_user_model()

def index(request):
    context = {}
    return render(request, 'chatIndex.html', context)