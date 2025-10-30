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
	inputChar = '|'


	match commandArgs[0]:
		case 'info':
			if len(commandArgs) == 1:
				msg = 'Put what you want info about after a colon'

			else:
				match commandArgs[1]:
					case s if s.startswith('user'):
						try:
							user = commandArgs[1].split(inputChar)[1]
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

					case s if s.startswith('post'):
						match commandArgs[2]:
							case s if s.startswith('from'):
								try:
									user = commandArgs[2].split(inputChar)[1]
									userInfo = User.objects.get(username=user)
									posts = Post.objects.filter(author=userInfo.username)
									if posts.count() == 0:
										msg = f"{user} has not made any posts yet"
									else:
										items = [f'[{p.id}], title: {p.title}' for p in posts]
										msg = f"Posts by {user}:\n" + "\n".join(items)

								except models.CustomUser.DoesNotExist as e:
									msg = f'User "{user}" not found\n Error: {e}'
								
								except IndexError as e:
									msg = f'Posts by who?'

							case s if s.startswith('id'):
								id = commandArgs[2].split(inputChar)[1]
								post = Post.objects.get(id=id)
								msg = f'''Post {id}, posted by {post.author}
								The title is "{post.title}", the body of the post is as follows\n
								{post.body}'''

							case _:
								msg = "Make sure to say how you want to search"

					case s if s.startswith('video'):
						match commandArgs[2]:
							case s if s.startswith('from'):
								try:
									user = commandArgs[2].split(inputChar)[1]
									userInfo = User.objects.get(username=user)
									videos = Video.objects.filter(author=userInfo.username)
									if videos.count() == 0:
										msg = f"{user} has not posted any videos yet"
									else:
										items = [f'[{p.id}], title: {p.title}' for p in videos]
										msg = f"Videos by {user}:\n" + "\n".join(items)

								except models.CustomUser.DoesNotExist as e:
									msg = f'User "{user}" not found\n Error: {e}'
								
								except IndexError as e:
									msg = f'Videos by who?'

							case s if s.startswith('id'):
								id = commandArgs[2].split(inputChar)[1]
								video = Video.objects.get(id=id)
								if video.likes == 1:
									like = ''
								else:
									like = 's'
								if video.views == 1:
									view = ''
								else:
									view = 's'

								msg = f'''VIdeo {id}, posted by {video.author}
								The title is "{video.title}", 
								It has {video.likes} like{like}, and {video.views} view{view}.
								The description of the video is as follows\n
								{video.description}'''

							case _:
								msg = "Make sure to say how you want to search"


					case _:
						msg = "What would you like information about?"
		
		case 'create':
			if len(commandArgs) == 1:
				msg = 'Put what you want to create after a colon'
			else:
				match commandArgs[1]:
					case 'post':
						try:
							match commandArgs[2]:
								case s if s.startswith('title'):
									title = commandArgs[2].split(inputChar)[1]

								case s if s.startswith('body'):
									body = commandArgs[2].split(inputChar)[1]

								case _:
									msg = 'This command only supports body and title'
							
							match commandArgs[3]:
								case s if s.startswith('title'):
									title = commandArgs[3].split(inputChar)[1]

								case s if s.startswith('body'):
									body = commandArgs[3].split(inputChar)[1]

								case _:
									msg = 'This command only supports body and title'

							msg = f'Created Post with\nTitle: {title}\nBody: {body}'
							post = Post(
								author=User.objects.get(username=from_user),
								title=title,
								body=body + '<br><br><small><i>Created using Commands</i></small>',
							).save()
							msg = msg

						except IndexError as e:
							msg = 'Be sure to add the body and title'

					case 'video':
						msg = 'You cannot create videos thrugh commands yet'

					case 'comment':
						try:
							match commandArgs[2]:
								case s if s.startswith('type'):
									commentType = commandArgs[2].split(inputChar)[1]

									if commentType == 'video':
										msg = 'Making a comment on a video I see'
									elif commentType == 'post':
										msg = 'Making a comment on a post I see'
									else:
										msg = "You must specify what type of comment you are making"
								case _:
									msg = 'You can create posts and comments'

						except IndexError as e:
							msg = 'Be sure to add the type, id, and body'

		case _:
			msg = 'You can use the ! character to run commands'
			
	print(commandArgs)
	newMessage(msg, from_user)
	return msg