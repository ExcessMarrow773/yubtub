from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.utils import ProgrammingError
from django.db.models import Q

from app.forms import PostVideo, VideoCommentForm, CreatePost, PostCommentForm
from app.models import Video, VideoComment, Post, PostComment

from itertools import chain
from operator import attrgetter
from datetime import timedelta

from app import mail
from app.qol import isVMuted, isPMuted, isMuted

from accounts.models import CustomUser

import os
import json

User = get_user_model()
# Create your views here.

def getUserFromID(id):
	try:
		return User.objects.get(id=id)
	except CustomUser.DoesNotExist:
		return User.objects.get(id=1)

@xframe_options_exempt
def index(request):
	user_videos = Video.objects.order_by('-created_on').filter(created_on__gt=timezone.now() - timedelta(weeks=1))
	user_posts = Post.objects.order_by('-created_on').filter(created_on__gt=timezone.now() - timedelta(weeks=1))
	old_user_videos = Video.objects.order_by('-created_on')
	old_user_posts = Post.objects.order_by('-created_on')
	
	user = getUserFromID(request.user.pk)

	# Combine and sort by created_on
	combined = sorted(
		chain(user_videos, user_posts),
		key=attrgetter('created_on'),
		reverse=True
	)

	old_combined = sorted(
		chain(list(set(old_user_videos) - set(user_videos)), list(set(old_user_posts) - set(user_posts))),
		key=attrgetter('created_on'),
		reverse=True
	)

	context = {
		'combined': combined,
		'old_combined': old_combined,
	}
	return render(request, 'index.html', context)

@login_required
def editPost(request, pk):
	post = get_object_or_404(Post, id=pk)
	user = getUserFromID(request.user.id)

	if user.id != post.author:
		return redirect('app:post', pk)

	if request.method == "POST":
		form = CreatePost(request.POST, request.FILES)
		if form.is_valid():
			post.author=user.id
			post.title=form.cleaned_data["title"]
			post.body=form.cleaned_data["body"]
			if form.cleaned_data["images"] is not None:
				post.images=form.cleaned_data["images"]
			post.image_size=form.cleaned_data["image_size"]
			post.save()
			mentions = post.get_valid_mentions()
			if mentions:
				mail.mention_email(mentions, post, 'post')
			return redirect('app:post', pk)
	else:
		form = CreatePost(
			initial={
				'title': post.title,
				'body': post.body,
				'images': post.images,
				'image_size': post.image_size
			})

	context = {
		'post': post,
		'form': form
	}
	return render(request, 'app/editPost.html', context)

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

	context = {
		'form': form,
		'uploadForm': None
	}
	return render(request, 'createVideo.html', context)

@login_required
def editVideo(request, pk):
	video = get_object_or_404(Video, id=pk)
	user = getUserFromID(request.user.id)

	if user.id != video.author:
		return redirect('app:watch', pk)

	if request.method == "POST":
		form = PostVideo(request.POST, request.FILES)
		if form.is_valid():
			video.author=user.id
			video.title=form.cleaned_data["title"]
			video.description=form.cleaned_data["description"]
			if form.cleaned_data["video"] is not None:
				video.video_file=form.cleaned_data["video_file"]
			if form.cleaned_data["thumbnail"] is not None:
				video.thumbnail=form.cleaned_data["thumbnail"]

			video.save()
			mentions = video.get_valid_mentions()
			if mentions:
				mail.mention_email(mentions, video, 'video')
			return redirect('app:watch', pk)
	else:
		form = PostVideo(
			initial={
				'title': video.title,
				'description': video.description,
				'thumbnail': video.thumbnail,
				'video_file': video.video_file
			})

	context = {
		'video': video,
		'form': form
	}
	return render(request, 'app/editVideo.html', context)

def watchVideo(request, pk):
	video = get_object_or_404(Video, pk=pk)
	likes = video.likes
	if request.user.is_authenticated:
		try:
			# FIX: compare User objects, not int vs queryset of Users
			if not video.viewedUsers.filter(pk=request.user.pk).exists():
				video.viewedUsers.add(request.user)
				video.views += 1
				video.save()
		except ProgrammingError as e:
			print(e)

	if request.method == "POST":
		form = VideoCommentForm(request.POST)
		if form.is_valid():
			user = User.objects.get(username=request.user.username)
			comment = VideoComment(
				author=user.id,
				body=form.cleaned_data["body"],
				video=video
			)
			comment.save()

			mentions = comment.get_valid_mentions()
			if mentions:
				mail.mention_email(mentions, comment, 'message')
				print(f"Mentioned users: {mentions}")
	else:
		form = VideoCommentForm()

	comments = VideoComment.objects.filter(video=video).order_by("-created_on")


	videoAuthor = User.objects.get(id=video.author).username

	context = {
		'videos': video,
		'pk': pk,
		'comments': comments,
		'likes': likes,
		'form': form,
		'muted': isMuted(request),
		'videoAuthor': videoAuthor
	}

	return render(request, 'watch.html', context)

def githubRedirect(request):
	context = {}
	return render(request, 'githubRedirect.html', context)

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

def DEMO(request):
	file_path = os.path.join(os.path.dirname(__file__), '../markdownFiles/DEMO.md')
	with open(file_path, 'r') as f:
		markdown_content = f.read()
	
	context = {
		'mdHelp': markdown_content,
	}
	return render(request, "app/mdHelp.html", context)

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
				image_size=form.cleaned_data["image_size"]
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
	url = request.build_absolute_uri()
	user = getUserFromID(request.user.pk)
	if request.method == "POST":
		form = PostCommentForm(request.POST)
		if form.is_valid():
			
			comment = PostComment(
				author=user.id,
				body=form.cleaned_data["body"],
				post=post,
			)
			comment.save()

			mentions = comment.get_valid_mentions()
			if mentions:
				mail.mention_email(mentions, comment, 'message', url=url)
				print(f"Mentioned users: {mentions}")

			return HttpResponseRedirect(request.path_info)
	comments = PostComment.objects.filter(post=post)

	postAuthor = User.objects.get(id=post.author).username
	
	superUsers = User.objects.filter(is_superuser=True).all()
	superUserIds = []
	for i in superUsers:
		superUserIds.append(i.id)


	context = {
		"post": post,
		"comments": comments,
		"form": PostCommentForm(),
		"muted": isMuted(request),
		'postAuthor': postAuthor,
		'superUsers': superUsers,
		'superUserIds': superUserIds
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
		following_names.append(i.id)

	posts = Post.objects.filter(author__in=following_names).order_by('-created_on')
	videos = Video.objects.filter(author__in=following_names).order_by('-created_on')
	combined = sorted(
		chain(posts, videos),
		key=attrgetter('created_on'),
		reverse=True
	)
	
	
	context = {
		'combined': combined,
		'following': following
	}

	return render(request, "app/following.html", context)

def search(request):
	query = request.GET.get("q")

	if not query:
		query = ""

	filter_query_p = Q(title__icontains=query) | Q(body__icontains=query)
	filter_query_v = Q(title__icontains=query) | Q(description__icontains=query)

	posts = Post.objects.filter(filter_query_p).order_by("-created_on")
	videos = Video.objects.filter(filter_query_v).order_by("-created_on")
	combined = sorted(
		chain(posts, videos),
		key=attrgetter('created_on'),
		reverse=True
	)


	context = {
		'combined': combined,
	}

	return render(request, "app/search.html", context)

## API REQUESTS

def uploadSong(request):
	context = {}
	return render(request, "app/songUpload.html", context)

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

def handler405(request, exception=None):
	return render(request, '405.html', status=405)