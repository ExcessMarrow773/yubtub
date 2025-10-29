from django.contrib.auth import get_user_model
from accounts import models
from .models import Message
from app.models import Post, Video
User = get_user_model()

def newMessage(msg, from_user):
	message = Message(
		from_user=User.objects.get(username='system'),
		to_user=from_user,
		body=msg
	)
	message.save()

	return message

def command(body, from_user):
	command = body[1:]
	commandArgs = command.split(':')
	match commandArgs[0]:
		case 'info':
			if len(commandArgs) == 1:
				msg = 'Put what you want info about after a colon'
			else:
				match commandArgs[1]:
					case s if s.startswith('user'):
						try:
							user = commandArgs[1].split('`')[1]
							userInfo = User.objects.get(username=user)
							posts_count = len(Post.objects.filter(author=userInfo.username).all())
							videos_count = len(Video.objects.filter(author=userInfo.username).all())
							messages_sent_count = len(Message.objects.filter(from_user=from_user).all())
							messages_receved_count = len(Message.objects.filter(to_user=from_user).all())
							msg = (f"Information about user: \"{userInfo.username}\"\n"
								f"User ID: {userInfo.id}\n"
								f"{userInfo.username} has made {posts_count} posts\n"
								f"{userInfo.username} has posted {videos_count} videos\n"
								f"{userInfo.username} has sent {messages_sent_count} messages\n"
								f"{userInfo.username} has receved {messages_receved_count} messages")
						except models.CustomUser.DoesNotExist as e:
							msg = f'User "{user}" not found\n Error: {e}'
						except IndexError as e:
							print(commandArgs)
							msg = f'Please specify a user\n {e}'
		
		case _:
			msg = 'You can use the ! character to run commands'
		
	newMessage(msg, from_user)
	return msg