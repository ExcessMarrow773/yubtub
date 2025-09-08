from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from app.forms import PostVideo
from app.models import Video, Comment
# Create your views here.

def index(request):
    context = {
    }
    return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def postVideo(request):
    if request.method == "POST":
        form = PostVideo(request.POST, request.FILES)
        if form.is_valid():
            video = Video(
                author=request.user.username,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                thumbnail=form.cleaned_data["thumbnail"],
                video=form.cleaned_data["image"]
            )
            video.save()
            return redirect('index')
    else:
        form = PostVideo()
    
    return render(request, 'video.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    template_name = 'index.html'