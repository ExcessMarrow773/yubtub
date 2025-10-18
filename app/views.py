from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from app.forms import PostVideo, VideoCommentForm, CreatePost, PostCommentForm, CustomAuthenticationForm, CustomUserCreationForm
from app.models import Video, VideoComment, Post, PostComment
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from itertools import chain
from operator import attrgetter
import os
import json

User = get_user_model()
# Create your views here.

def index(request):
    context = {
        'videos': Video.objects.all().order_by('-created_on'),
    }
    return render(request, 'index.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()         # important — saves hashed password
            login(request, user)       # optional: log user in immediately
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
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
    if not request.user in videos.viewedUsers.all():
        videos.viewedUsers.add(request.user)
        videos.views += 1
    videos.save()

    if request.method == "POST":
        form = VideoCommentForm(request.POST)
        if form.is_valid():
            comment = VideoComment(
                author=request.user.username,
                body=form.cleaned_data["body"],
                video=videos
            )
            comment.save()
    else:
        form = VideoCommentForm()

    comments = VideoComment.objects.filter(video=videos).order_by("-created_on")
    context = {
        'videos': videos,
        'pk': pk,
        'comments': comments,
        'likes': likes,
        'form': form
    }

    return render(request, 'watch.html', context)

def account(request, username):
    user_videos = Video.objects.filter(author=username).order_by('-created_on')
    user_posts = Post.objects.filter(author=username).order_by('-created_on')

    # Combine and sort by created_on
    combined = sorted(
        chain(user_videos, user_posts),
        key=attrgetter('created_on'),
        reverse=True
    )

    following = request.user.following.all()
    print(following)

    following_names = []
    for i in following:
    	following_names.append(i.username)
    print(following_names)

    context = {
        'combined': combined,
        'username': username,
        'isUsersAccount': username == request.user.username,
        'followingUser': username in following_names
    }
    return render(request, 'account.html', context)

def TODO(request):
    file_path = os.path.join(os.path.dirname(__file__), '../TODO.md')
    with open(file_path, 'r') as f:
        markdown_content = f.read()
    context = {
        'TODO': markdown_content,
    }
    return render(request, 'app/TODO.html', context)

def cornhub(request):
    context = {}
    return render(request, 'app/cornhub.html', context)

@login_required
def makePost(request):
    if request.method == "POST":
        form = CreatePost(request.POST, request.FILES)
        if form.is_valid():
            post = Post(
                author=request.user.username,
                title=form.cleaned_data["title"],
                body=form.cleaned_data["body"],
            )
            post.save()
            return redirect('index')
    else:
        form = CreatePost()
    context = {
        'form': form
    }
    return render(request, 'app/makePost.html', context)

def postIndex(request):
    posts = Post.objects.all().order_by("-created_on")
    context = {
        "posts": posts,
    }
    return render(request, "app/postIndex.html", context)

def viewPost(request, pk):
    post = Post.objects.get(pk=pk)
    form = PostCommentForm()
    if request.method == "POST":
        form = PostCommentForm(request.POST)
        if form.is_valid():
            comment = PostComment(
                author=request.user.username,
                body=form.cleaned_data["body"],
                post=post,
            )
            comment.save()
            return HttpResponseRedirect(request.path_info)
    comments = PostComment.objects.filter(post=post)
    context = {
        "post": post,
        "comments": comments,
        "form": PostCommentForm(),
    }

    return render(request, "app/viewPost.html", context)


def mdHelp(request):
	file_path = os.path.join(os.path.dirname(__file__), '../markdownFiles/help.md')
	with open(file_path, 'r') as f:
		markdown_content = f.read()

	context = {
		"mdHelp": markdown_content,
	}
	return render(request, "app/mdHelp.html", context)

def following(request):
	user = get_object_or_404(User, username=request.user.username)
	following = user.following.all()

	following_names = []
	for i in following:
		following_names.append(i.username)

	posts = Post.objects.filter(author__in=following_names).order_by('-created_on')
	videos = Video.objects.filter(author__in=following_names).order_by('-created_on')

	if len(following) > 10:
		following = following[:10]
	if len(posts) > 10:
		posts = posts[:10]
	if len(videos) > 10:
		videos = videos[:10]
	context = {
		'following': following,
		'posts': posts
	}

	return render(request, "app/following.html", context)

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

#@csrf_exempt
@require_POST
def follow_user(request):
	if not request.user.is_authenticated:
		return JsonResponse({'message': 'Login required'}, status=403)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': 'Invalid JSON'}, status=400)


	username=data.get('account')
	print(request.user.is_authenticated)

	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return JsonResponse({'message': 'User not found.'}, status=404)

	if request.user in user.followers.all():
		request.user.unfollow(user)
		return JsonResponse({'message': 'Sad to see you go!', 'following': False})
	else:
		request.user.follow(user)
		return JsonResponse({'message': 'Thanks for following!', 'following': True})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm

class CustomLogoutView(LogoutView):
    template_name = 'index.html'