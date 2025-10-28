from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

def newMessage(msg, from_user):
	message = Message(
		from_user=User.objects.get(username='system'),
		to_user=from_user,
		body=msg
	)
	message.save()

	print(message)
	return message

def command(body, from_user):
	command = body[1:]
	print(command)
	match command:
		case 'info':
			try:
				if command[5] != ':':
					newMessage('command malformed\n try again', from_user)
					return 'command malformed\n try again'
			except IndexError:
					newMessage('command malformed\n try again', from_user)
					return 'command malformed\n try again'
			
