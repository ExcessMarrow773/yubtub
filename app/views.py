from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from app.forms import PostVideo, VideoCommentForm, CreatePost, PostCommentForm, CustomAuthenticationForm, CustomUserCreationForm
from app.models import Video, VideoComment, Post, PostComment

from itertools import chain
from operator import attrgetter

from app import mail
from app.qol import isVMuted, isPMuted, isMuted

import os
import json

User = get_user_model()
# Create your views here.

def getUserFromID(id):
    User.objects.get(id=id)

def index(request):
    user_videos = Video.objects.order_by('-created_on')
    user_posts = Post.objects.order_by('-created_on')

    # Combine and sort by created_on
    combined = sorted(
        chain(user_videos, user_posts),
        key=attrgetter('created_on'),
        reverse=True
    )

    authors = {}
    for i in combined:
        user = User.objects.get(id=i.author).username
        authors[i.author] = user
        
    context = {
        'combined': combined,
        'authors': authors,
    }
    return render(request, 'index.html', context)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()         # important — saves hashed password
            login(request, user)       # optional: log user in immediately
            return redirect('app:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def postVideo(request):
    if isVMuted(request) or isMuted(request):
        return redirect('app:index')

    if request.method == "POST":
        form = PostVideo(request.POST, request.FILES)
        if form.is_valid():
            video = Video(
                author=request.user.pk,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                thumbnail=form.cleaned_data["thumbnail"],
                video_file=form.cleaned_data["video_file"],
            )
            video.save()
            mentions = video.get_valid_mentions()
            if mentions:
                mail.mention_email(mentions, video, 'desc')
            return redirect('app:index')
    else:
        form = PostVideo()

    return render(request, 'createVideo.html', {'form': form})

def watchVideo(request, pk):
    videos = get_object_or_404(Video, pk=pk)
    likes = videos.likes
    user = get_object_or_404(User, id=request.user.id)
    if request.user.is_authenticated:
        print("Authenticated")
        if not (user in videos.viewedUsers.all()):
            videos.viewedUsers.add(user)
            videos.views += 1
    else:
        print("Not Authenticated")
    videos.save()

    if request.method == "POST":
        form = VideoCommentForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            comment = VideoComment(
                author=user.id,
                body=form.cleaned_data["body"],
                video=videos
            )
            comment.save()

            mentions = comment.get_valid_mentions()
            if mentions:
                mail.mention_email(mentions, comment, 'message')
                print(f"Mentioned users: {mentions}")
    else:
        form = VideoCommentForm()

    comments = VideoComment.objects.filter(video=videos).order_by("-created_on")

    authors = {}
    for i in comments:
        user = User.objects.get(id=i.author).username
        authors[i.author] = user

    videoAuthor = User.objects.get(id=videos.author).username

    context = {
        'videos': videos,
        'pk': pk,
        'comments': comments,
        'likes': likes,
        'form': form,
        'muted': isMuted(request),
        'authors': authors,
        'videoAuthor': videoAuthor
    }

    return render(request, 'watch.html', context)

def account(request, pk):
    user_videos = Video.objects.filter(author=pk).order_by('-created_on')
    user_posts = Post.objects.filter(author=pk).order_by('-created_on')

    # Combine and sort by created_on
    combined = sorted(
        chain(user_videos, user_posts),
        key=attrgetter('created_on'),
        reverse=True
    )
    if request.user.is_authenticated:
        following = request.user.following.all()
    else:
        following = []

    following_names = []
    for i in following:
        following_names.append(i.username)
    user = get_object_or_404(User, id=pk)
    context = {
        'combined': combined,
        'username': user,
        'isUsersAccount': user.username == request.user.username,
        'followingUser': user.username in following_names,
        'user': request.user
    }
    return render(request, 'app/account.html', context)

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
    if isPMuted(request) or isMuted(request):
         return redirect('app:index')
    if request.method == "POST":
        form = CreatePost(request.POST, request.FILES)
        if form.is_valid():
            post = Post(
                author=request.user.pk,
                title=form.cleaned_data["title"],
                body=form.cleaned_data["body"],
                images=form.cleaned_data["images"],
            )
            post.save()
            mentions = post.get_valid_mentions()
            if mentions:
                mail.mention_email(mentions, post, 'post')
            return redirect('app:index')
    else:
        form = CreatePost()
    context = {
        'form': form
    }
    return render(request, 'app/makePost.html', context)

def viewPost(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostCommentForm()

    if request.method == "POST":
        form = PostCommentForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            comment = PostComment(
                author=user.id,
                body=form.cleaned_data["body"],
                post=post,
            )
            comment.save()

            mentions = comment.get_valid_mentions()
            if mentions:
                mail.mention_email(mentions, comment, 'message')
                print(f"Mentioned users: {mentions}")

            return HttpResponseRedirect(request.path_info)
    comments = PostComment.objects.filter(post=post)

    authors = {}
    for i in comments:
        user = User.objects.get(id=i.author).username
        authors[i.author] = user

    postAuthor = User.objects.get(id=post.author).username

    context = {
        "post": post,
        "comments": comments,
        "form": PostCommentForm(),
        "muted": isMuted(request),
        'authors': authors,
        'postAuthor': postAuthor
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

def EconProject(request):
    file_path = os.path.join(os.path.dirname(__file__), '../markdownFiles/EconProject.md')
    with open(file_path, 'r') as f:
        markdown_content = f.read()
    
    context = {
        'mdHelp': markdown_content,
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
        video.likedUsers.remove(request.user)
        video.likes -= 1
        video.save()
        return JsonResponse({'message': 'You unliked this video.', 'likes': video.likes}, status=200)
    else:
        video.likedUsers.add(request.user)
        video.likes += 1
        video.save()
        return JsonResponse({'message': 'Thanks for liking!', 'likes': video.likes}, status=200)
 
@require_POST
def follow_user(request):
	if not request.user.is_authenticated:
		return JsonResponse({'message': 'Login required'}, status=403)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': 'Invalid JSON'}, status=400)


	username=data.get('account')

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

def handler405(request, exception=None):
	return render(request, '405.html', status=405)