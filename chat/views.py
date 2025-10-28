from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from operator import attrgetter
from itertools import chain
import json

from chat.models import Message
import chat.bot as bot
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
	this_user = request.user

	message_to_user = Message.objects.all().filter(to_user=this_user.pk, from_user=other_user.pk)
	message_from_user = Message.objects.all().filter(from_user=this_user.pk, to_user=other_user.pk)

	messages = sorted(
        chain(message_from_user, message_to_user),
        key=attrgetter('sent_on'),
        reverse=False
    )

	context = {
		'account': other_user,
		'username': this_user.username,
		'this_user': this_user,
		'messages': messages
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
	dateTime = data.get('dateTime')
	things = {'data': data, 'to_user_data': to_user_data, 'from_user_data': from_user_data, 'dateTime': dateTime}

	to_user = get_object_or_404(User, username=to_user_data)
	from_user = get_object_or_404(User, username=from_user_data)

	message = Message(
		from_user=from_user,
		to_user=to_user,
		body=msg
	)
	
	if msg.startswith('!'):
		bot_response = bot.command(msg, from_user)

	message.save()
	if bot_response != None:
		return JsonResponse({'type': 'bot_response','message': bot_response}, status=200)
	return JsonResponse({'message': msg}, status=200)