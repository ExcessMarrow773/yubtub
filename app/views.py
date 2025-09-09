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
                video_file=form.cleaned_data["video"],
                posted_on=form.cleaned_data["schedulePost"] if form.cleaned_data["schedulePost"] else None
            )
            video.save()
            return redirect('index')
    else:
        form = PostVideo()
    
    return render(request, 'video.html', {'form': form})

def watchVideo(request, pk):
    videos = Video.objects.get(pk=pk)
    # comments = Comment.objects.get(video=videos)
    context = {
        'videos': videos,
        'pk': pk,
        # 'comments': comments
    }
    return render(request, 'watch.html', context)

def account(request, username):
    user_videos = Video.objects.filter(author=username).order_by('-posted_on')
    context = {
        'user_videos': user_videos,
        'username': username
    }
    return render(request, 'account.html', context)

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    template_name = 'index.html'