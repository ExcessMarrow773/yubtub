from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from app.forms import PostVideo, CommentForm
from app.models import Video, Comment
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

def index(request):
    context = {
        'videos': Video.objects.all().order_by('-posted_on')
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
        print(request.POST)
        if form.is_valid():
            video = Video(
                author=request.user.username,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                thumbnail=form.cleaned_data["thumbnail"],
                video_file=form.cleaned_data["video_file"],
            )
            video.save()
            return redirect('index')
    else:
        form = PostVideo()

    return render(request, 'createVideo.html', {'form': form})

def watchVideo(request, pk):
    videos = Video.objects.get(pk=pk)
    likes = videos.likes
    videos.views += 1
    videos.save()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=request.user.username,
                body=form.cleaned_data["body"],
                video=videos
            )
            comment.save()
    else:
        form = CommentForm()

    comments = Comment.objects.filter(video=videos).order_by("-created_on")
    context = {
        'videos': videos,
        'pk': pk,
        'comments': comments,
        'likes': likes,
        'form': form
    }

    return render(request, 'watch.html', context)

def account(request, username):
    user_videos = Video.objects.filter(author=username).order_by('-posted_on')
    context = {
        'user_videos': user_videos,
        'username': username
    }
    return render(request, 'account.html', context)

@csrf_exempt  # For production: use @require_POST and handle CSRF with token properly
@require_POST
def like_video(request):
    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Login required.'}, status=403)

    data = json.loads(request.body)
    video_id = data.get('video_id')

    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return JsonResponse({'message': 'Video not found.'}, status=404)

    if request.user in video.likedUsers.all():
        return JsonResponse({'message': 'You already liked this video.', 'liked': False, 'alreadyLiked': True})

    video.likedUsers.add(request.user)
    video.likes += 1
    video.save()
    return JsonResponse({'message': 'Thanks for liking!', 'liked': True, 'alreradyLiked': False})

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(LogoutView):
    template_name = 'index.html'