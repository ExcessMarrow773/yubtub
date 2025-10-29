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
	commandLen = len(command)
	commandArgs = command.split(':')
	commandArgsLen = len(commandArgs)
	print(commandArgs)
	match commandArgs[0]:
		case 'info':
			try:
				if len(commandArgs) == 1:
					msg = 'Command malformed\n Try again'
					newMessage(msg, from_user)
					return msg
				
				match commandArgs[1]:
					case '':
						msg = 'Info about what?'
						newMessage(msg, from_user)
						return msg
					
					case s if s.startswith('user'):
						print('thing')
						try:
							user = commandArgs[1].split('"')[1]
							userInfo = User.objects.get(username=user)
							posts_count = Post.objects.filter(author=userInfo.username).count()
							videos_count = Video.objects.filter(author=userInfo.username).count()
							msg = (f"Information about user: \"{userInfo.username}\"\n"
								f"User ID: {userInfo.id}\n"
								f"{userInfo.username} has made {posts_count} posts\n"
								f"{userInfo.username} has posted {videos_count} videos")
						except models.CustomUser.DoesNotExist as e:
							msg = f'User "{user}" not found\n Error: {e}'
						except IndexError:
							msg = f'Please specify a user'
						newMessage(msg, from_user)
						return msg
					
					case 'post':
						if commandArgsLen > 2:
							if commandArgs[2][:4] == 'from':
								username = commandArgs[2].split('"')[1]
								posts_qs = Post.objects.filter(author=username)
								if posts_qs.exists():
									items = [f'[{p.id}], title: {p.title}' for p in posts_qs]
									msg = f"Posts by {username}:\n" + "\n".join(items)
								else:
									msg = f'No posts found for "{username}"'
							elif commandArgs[2][:2] == 'id':
								id = commandArgs[2].split('"')[1]
								post = Post.objects.get(id=id)
								msg = f'''Post {id}, posted by {post.author}
								The title is "{post.title}", the body of the post is as follows
								{post.body}'''
							else:
								msg = 'Make sure to say the way to search the posts'
						else:
							msg = "What info about posts do you want?"
						newMessage(msg, from_user)
						return msg
					
					case 'video':
						print(commandArgs)
						if commandArgs[2][:4] == 'from':
							msg = 'test'
						else:
							msg = "What info about videos do you want?"


					case _:
						msg = 'Put the thing you want information on after the colon'
						newMessage(msg, from_user)
						return msg
				

			except IndexError as e:
					newMessage(str(e), from_user)
					return str(e)

		case _:
			msg = 'Huh?'
			newMessage(msg, from_user)
			return msg
			
