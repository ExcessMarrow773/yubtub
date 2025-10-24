from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

import json

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

@require_POST
def sendMsg(request):
	if not request.user.is_authenticated:
		return JsonResponse({'message': 'Login required'}, status=403)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': 'Invalid JSON'}, status=400)


	msg=data.get('msg')
	to = data.get('to')

	return JsonResponse({'message': msg, 'to': to}, status=200)