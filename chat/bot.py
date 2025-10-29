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
	# bind args safely so we can use guards without slicing and risking IndexError
	arg0 = commandArgs[0] if commandArgsLen > 0 else ''
	arg1 = commandArgs[1] if commandArgsLen > 1 else ''
	arg2 = commandArgs[2] if commandArgsLen > 2 else ''
	match arg0:
		case 'info':
			try:
				if commandArgsLen == 1:
					msg = 'Command malformed\n Try again'
					newMessage(msg, from_user)
					return msg
				match arg1:
					case s if s == '':
						msg = 'Info about what?'
						newMessage(msg, from_user)
						return msg
					case s if s.startswith('user'):
						# parse username from the argument (expecting user"name")
						try:
							# support either 'user"name"' or separated ':user:"name"' where the quoted name may be arg2
							if '"' in s:
								user = s.split('"')[1]
							elif arg2 and '"' in arg2:
								user = arg2.split('"')[1]
							else:
								raise IndexError('username not provided')
							userInfo = User.objects.get(username=user)
							posts_count = Post.objects.filter(author=userInfo.username).count()
							videos_count = Video.objects.filter(author=userInfo.username).count()
							msg = (f"Information about user: \"{userInfo.username}\"\n"
								f"User ID: {userInfo.id}\n"
								f"{userInfo.username} has made {posts_count} posts\n"
								f"{userInfo.username} has posted {videos_count} videos")
						except (IndexError, models.CustomUser.DoesNotExist) as e:
							msg = f'User not found or malformed argument: {e}'
						newMessage(msg, from_user)
						return msg
					case s if s.startswith('post'):
						if commandArgsLen > 2:
							# use arg2 safely
							if arg2.startswith('from'):
								try:
									username = arg2.split('"')[1]
									posts_qs = Post.objects.filter(author=username)
									if posts_qs.exists():
										items = [f'[{p.id}], title: {p.title}' for p in posts_qs]
										msg = f"Posts by {username}:\n" + "\n".join(items)
									else:
										msg = f'No posts found for "{username}"'
								except IndexError:
									msg = 'Malformed from argument. Use from"username"'
							elif arg2.startswith('id'):
								try:
									id = arg2.split('"')[1]
									post = Post.objects.get(id=id)
									msg = (f"Post {id}, posted by {post.author}\n"
										f"The title is \"{post.title}\", the body of the post is as follows\n"
										f"{post.body}")
								except (IndexError, Post.DoesNotExist):
									msg = f'Post with id not found or malformed id argument'
							else:
								msg = 'Make sure to say the way to search the posts'
						else:
							msg = "What info about posts do you want?"
						newMessage(msg, from_user)
						return msg
					case s if s.startswith('video'):
						# simple placeholder for video info; extend similarly to posts above
						if arg2.startswith('from'):
							msg = 'video: from handling not implemented yet'
						else:
							msg = "What info about videos do you want?"
						newMessage(msg, from_user)
						return msg
					case _:
						msg = 'Put the thing you want information on after the colon'
						newMessage(msg, from_user)
						return msg
				

			except IndexError as e:
					newMessage('command malformed\n try again', from_user)
					return str(e)

		case _:
			msg = 'Huh?'
			newMessage(msg, from_user)
			return msg
			
