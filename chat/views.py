from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

import json

from chat.models import Message
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
	other_user = get_object_or_404(User, username=account)
	this_user = request.user.username
	context = {
		'account': other_user,
		'this_user': this_user
	}
	print(this_user, other_user)
	return render(request, 'chat.html', context)

@require_POST
def sendMsg(request):
	if not request.user.is_authenticated:
		return JsonResponse({'message': 'Login required'}, status=403)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': 'Invalid JSON'}, status=400)


	msg = data.get('msg')
	to_user_data = data.get('to')
	from_user_data = data.get('from')	

	things = {'data': data, 'to_user_data': to_user_data, 'from_user_data': from_user_data}
	print(things)

	to_user = get_object_or_404(User, username=to_user_data)
	from_user = get_object_or_404(User, username=from_user_data)

	message = Message(
		from_user=from_user,
		to_user=to_user,
		body=msg
	)
	message.save()

	print(message)

	return JsonResponse({'message': msg}, status=200)