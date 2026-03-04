from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

from chat.models import Message
from chat import bot as chat_bot
from app.models import Post, Video

User = get_user_model()


# ---------------------------------------------------------------------------
# Message model tests
# ---------------------------------------------------------------------------

class MessageModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')

    def test_message_creation(self):
        msg = Message.objects.create(
            from_user=self.user1, to_user=self.user2, body='Hello!'
        )
        self.assertEqual(msg.from_user, self.user1)
        self.assertEqual(msg.to_user,   self.user2)
        self.assertEqual(msg.body,      'Hello!')

    def test_message_str_method(self):
        msg = Message.objects.create(
            from_user=self.user1, to_user=self.user2, body='Test'
        )
        self.assertEqual(str(msg), f"Message {msg.id} from {self.user1} to {self.user2}")

    def test_message_ordering(self):
        msg1 = Message.objects.create(from_user=self.user1, to_user=self.user2, body='First')
        msg2 = Message.objects.create(from_user=self.user1, to_user=self.user2, body='Second')
        messages = list(Message.objects.all())
        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)


# ---------------------------------------------------------------------------
# Chat view tests
# ---------------------------------------------------------------------------

class ChatViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1  = User.objects.create_user(username='alice', password='pass123')
        self.user2  = User.objects.create_user(username='bob',   password='pass123')
        # Mutual follow → friends
        self.user1.follow(self.user2)
        self.user2.follow(self.user1)

    def test_chat_index_requires_login(self):
        # Not logged in → get_object_or_404 on AnonymousUser raises 404
        response = self.client.get(reverse('chat:index'))
        self.assertEqual(response.status_code, 404)

    def test_chat_index_displays_mutual_friends(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('chat:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bob')

    def test_chat_index_only_shows_mutual_followers(self):
        self.client.login(username='alice', password='pass123')
        charlie = User.objects.create_user(username='charlie', password='pass')
        self.user1.follow(charlie)   # alice → charlie but NOT mutual

        response = self.client.get(reverse('chat:index'))
        self.assertContains(response,    'bob')
        self.assertNotContains(response, 'charlie')

    def test_chat_view_accessible_when_logged_in(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('chat:chat', args=['bob']))
        self.assertEqual(response.status_code, 200)

    def test_chat_view_displays_conversation(self):
        self.client.login(username='alice', password='pass123')
        Message.objects.create(from_user=self.user1, to_user=self.user2, body='Hello Bob')
        Message.objects.create(from_user=self.user2, to_user=self.user1, body='Hi Alice')

        response = self.client.get(reverse('chat:chat', args=['bob']))
        self.assertContains(response, 'Hello Bob')
        self.assertContains(response, 'Hi Alice')

    def test_send_message_requires_authentication(self):
        response = self.client.post(
            reverse('chat:sendMsg'),
            data=json.dumps({'msg': 'Test', 'to': 'bob', 'from': 'alice'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_send_message_creates_message(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.post(
            reverse('chat:sendMsg'),
            data=json.dumps({'msg': 'Test message', 'to': 'bob', 'from': 'alice'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Message.objects.filter(
                from_user=self.user1, to_user=self.user2, body='Test message'
            ).exists()
        )

    def test_send_message_invalid_json(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.post(
            reverse('chat:sendMsg'),
            data='invalid json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


# ---------------------------------------------------------------------------
# Bot command tests
# ---------------------------------------------------------------------------

class BotCommandTests(TestCase):
    def setUp(self):
        self.system, _ = User.objects.get_or_create(
            username='system',
            defaults={'password': 'pw', 'is_active': False},
        )
        self.sender, _ = User.objects.get_or_create(
            username='sender', defaults={'password': 'pw'}
        )
        self.target, _ = User.objects.get_or_create(
            username='target', defaults={'password': 'pw'}
        )

        # Use integer PKs for author fields
        Post.objects.create(author=self.target.pk, title='First Post',  body='Hello')
        Post.objects.create(author=self.target.pk, title='Second Post', body='World')
        Video.objects.create(
            author=self.target.pk,
            title='Test Video',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
        )

    def test_info_user_command(self):
        res = chat_bot.command(f'!info:user|{self.target.username}', self.sender)
        self.assertIn('Information about user', res)
        self.assertIn(self.target.username, res)

    def test_info_user_nonexistent(self):
        res = chat_bot.command('!info:user|nonexistent', self.sender)
        self.assertIn('not found', res)

    def test_info_user_no_username(self):
        res = chat_bot.command('!info:user', self.sender)
        self.assertIn('specify a user', res)

    def test_info_post_from_user(self):
        res = chat_bot.command(f'!info:post:from|{self.target.username}', self.sender)
        self.assertIn(f'Posts by {self.target.username}', res)
        self.assertIn('First Post',  res)
        self.assertIn('Second Post', res)

    def test_info_post_from_user_no_posts(self):
        u = User.objects.create_user(username='noposts', password='pw')
        res = chat_bot.command(f'!info:post:from|{u.username}', self.sender)
        self.assertIn('has not made any posts yet', res)

    def test_info_post_by_id(self):
        post = Post.objects.filter(author=self.target.pk).first()
        res  = chat_bot.command(f'!info:post:id|{post.id}', self.sender)
        self.assertIn(f'Post {post.id}', res)
        self.assertIn(post.title, res)

    def test_info_video_from_user(self):
        res = chat_bot.command(f'!info:video:from|{self.target.username}', self.sender)
        self.assertIn(f'Videos by {self.target.username}', res)
        self.assertIn('Test Video', res)

    def test_info_video_from_user_no_videos(self):
        u = User.objects.create_user(username='novideos', password='pw')
        res = chat_bot.command(f'!info:video:from|{u.username}', self.sender)
        self.assertIn('has not posted any videos yet', res)

    def test_info_video_by_id(self):
        video = Video.objects.filter(author=self.target.pk).first()
        res   = chat_bot.command(f'!info:video:id|{video.id}', self.sender)
        self.assertIn('VIdeo', res)
        self.assertIn(video.title, res)

    def test_info_command_no_parameters(self):
        res = chat_bot.command('!info', self.sender)
        self.assertIn('what you want info about', res)

    def test_create_post_command(self):
        res = chat_bot.command(
            '!create:post:title|Test Title:body|Test Body', self.sender
        )
        self.assertIn('Created Post', res)
        self.assertIn('Test Title', res)
        self.assertTrue(
            Post.objects.filter(title='Test Title', author=self.sender).exists()
        )

    def test_create_post_missing_parameters(self):
        res = chat_bot.command('!create:post:title|Test Title', self.sender)
        self.assertIn('Be sure to add the body and title', res)

    def test_create_video_not_supported(self):
        res = chat_bot.command('!create:video', self.sender)
        self.assertIn('cannot create videos thrugh commands', res)

    def test_create_command_no_type(self):
        res = chat_bot.command('!create', self.sender)
        self.assertIn('what you want to create', res)

    def test_unknown_command(self):
        res = chat_bot.command('!unknown', self.sender)
        self.assertIn('use the ! character to run commands', res)

    def test_bot_creates_system_message(self):
        initial = Message.objects.count()
        chat_bot.newMessage('Test message', self.sender)
        self.assertEqual(Message.objects.count(), initial + 1)
        msg = Message.objects.latest('sent_on')
        self.assertEqual(msg.from_user, self.system)
        self.assertEqual(msg.to_user,   self.sender)
        self.assertEqual(msg.body,      'Test message')


# ---------------------------------------------------------------------------
# Bot integration tests
# ---------------------------------------------------------------------------

class BotIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.system, _ = User.objects.get_or_create(
            username='system',
            defaults={'password': 'pw', 'is_active': False},
        )
        self.user = User.objects.create_user(username='testuser', password='pass123')

    def test_bot_command_via_chat(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('chat:sendMsg'),
            data=json.dumps({'msg': '!info:user|testuser', 'to': 'system', 'from': 'testuser'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        if data.get('type') == 'bot_response':
            self.assertIn('Information about user', data['message'])

    def test_regular_message_to_system(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('chat:sendMsg'),
            data=json.dumps({'msg': 'Hello system', 'to': 'system', 'from': 'testuser'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())

    def test_command_to_non_system_user(self):
        other = User.objects.create_user(username='other', password='pass')
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(
            reverse('chat:sendMsg'),
            data=json.dumps({'msg': '!info:user|testuser', 'to': 'other', 'from': 'testuser'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())


# ---------------------------------------------------------------------------
# Message query tests
# ---------------------------------------------------------------------------

class MessageQueryTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user3 = User.objects.create_user(username='user3', password='pass')

    def test_filter_messages_between_two_users(self):
        Message.objects.create(from_user=self.user1, to_user=self.user2, body='1→2')
        Message.objects.create(from_user=self.user2, to_user=self.user1, body='2→1')
        Message.objects.create(from_user=self.user3, to_user=self.user1, body='3→1')

        messages = Message.objects.filter(
            from_user__in=[self.user1, self.user2],
            to_user__in=[self.user1, self.user2],
        )
        self.assertEqual(messages.count(), 2)

    def test_count_messages_sent_by_user(self):
        Message.objects.create(from_user=self.user1, to_user=self.user2, body='a')
        Message.objects.create(from_user=self.user1, to_user=self.user3, body='b')
        Message.objects.create(from_user=self.user2, to_user=self.user1, body='c')
        self.assertEqual(Message.objects.filter(from_user=self.user1).count(), 2)

    def test_count_messages_received_by_user(self):
        Message.objects.create(from_user=self.user1, to_user=self.user2, body='a')
        Message.objects.create(from_user=self.user3, to_user=self.user2, body='b')
        Message.objects.create(from_user=self.user2, to_user=self.user1, body='c')
        self.assertEqual(Message.objects.filter(to_user=self.user2).count(), 2)