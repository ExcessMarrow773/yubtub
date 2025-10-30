from django.test import TestCase
from django.contrib.auth import get_user_model

from chat import bot as chat_bot
from app.models import Post, Video


class BotCommandTests(TestCase):
	def setUp(self):
		User = get_user_model()
		# ensure system user exists because chat.bot.newMessage looks up 'system'
		self.system, _ = User.objects.get_or_create(username='system', defaults={'password':'pw'})
		# create sender/target users (use get_or_create in case signals/migrations already created them)
		self.sender, _ = User.objects.get_or_create(username='sender', defaults={'password':'pw'})
		self.target, _ = User.objects.get_or_create(username='target', defaults={'password':'pw'})

		# create a couple posts authored by the target (author stored as username string)
		Post.objects.create(author=self.target.username, title='First Post', body='Hello')
		Post.objects.create(author=self.target.username, title='Second Post', body='World')

	def test_info_user_returns_counts(self):
		cmd = f'!info:user:"{self.target.username}"'
		res = chat_bot.command(cmd, self.sender)
		self.assertIn('Information about user', res)
		self.assertIn(f'has made 2 posts', res)

	def test_info_post_from_lists_posts(self):
		cmd = f'!info:post:from"{self.target.username}"'
		res = chat_bot.command(cmd, self.sender)
		self.assertIn(f'Posts by {self.target.username}', res)
		self.assertIn('First Post', res)
		self.assertIn('Second Post', res)

	def test_malformed_info_command(self):
		res = chat_bot.command('!info', self.sender)
		self.assertIn('Command malformed', res)

