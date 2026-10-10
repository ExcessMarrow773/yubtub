from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUsernameValidatorTests(TestCase):
    """Test custom username validation"""
    
    def test_username_with_plus_allowed(self):
        user = User.objects.create_user(username='user+test', password='pass')
        self.assertEqual(user.username, 'user+test')

    def test_username_with_hyphen_allowed(self):
        user = User.objects.create_user(username='user-test', password='pass')
        self.assertEqual(user.username, 'user-test')

    def test_username_with_underscore_allowed(self):
        user = User.objects.create_user(username='user_test', password='pass')
        self.assertEqual(user.username, 'user_test')

    def test_username_with_numbers_allowed(self):
        user = User.objects.create_user(username='user123', password='pass')
        self.assertEqual(user.username, 'user123')


class FollowerCountTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass')
        self.user2 = User.objects.create_user(username='bob', password='pass')
        self.user3 = User.objects.create_user(username='charlie', password='pass')

    def test_follower_count_increases(self):
        initial_count = self.user1.follower_count()
        self.user2.follow(self.user1)
        # Refresh to get updated count
        self.assertEqual(self.user1.follower_count(), initial_count + 1)

    def test_user_can_follow_and_unfollow(self):
        self.user1.follow(self.user2)
        self.assertTrue(self.user1.is_following(self.user2))
        self.user1.unfollow(self.user2)
        self.assertFalse(self.user1.is_following(self.user2))

    def test_follower_count_multiple_followers(self):
        initial_count = self.user1.follower_count()
        self.user2.follow(self.user1)
        self.user3.follow(self.user1)
        self.assertEqual(self.user1.follower_count(), initial_count + 2)


class SystemUserSignalTests(TestCase):
    """Test that new users automatically follow the system account"""

    def setUp(self):
        if not User.objects.filter(username='system').exists():
            User.objects.create_user(username='system', password='systempass')

    def test_new_user_follows_system(self):
        system_user = User.objects.get(username='system')
        new_user = User.objects.create_user(username='newuser', password='pass')
        self.assertTrue(new_user.is_following(system_user))

    def test_system_follows_new_user(self):
        system_user = User.objects.get(username='system')
        new_user = User.objects.create_user(username='newuser', password='pass')
        self.assertTrue(system_user.is_following(new_user))

    def test_system_doesnt_follow_itself(self):
        system_user = User.objects.get(username='system')
        self.assertFalse(system_user.is_following(system_user))


class AccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.other_user = User.objects.create_user(username='bob', password='pass123')

    def test_register_view_renders(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_post_creates_user(self):
        response = self.client.post(
            reverse('accounts:register'),
            data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'strongpass123',
                'password2': 'strongpass123',
            },
        )
        self.assertRedirects(response, reverse('app:index'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_authenticates_user(self):
        response = self.client.post(
            reverse('accounts:login'),
            data={'username': 'alice', 'password': 'pass123'},
        )
        self.assertIn(response.status_code, (302, 303))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_settings_view_requires_login(self):
        response = self.client.get(reverse('accounts:settings'))
        self.assertIn(response.status_code, (302, 303))

    def test_settings_post_updates_profile(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.post(
            reverse('accounts:settings'),
            data={
                'first_name': 'Alice',
                'last_name': 'Wonder',
                'description': 'Hello there',
                'email': 'alice@example.com',
            },
        )
        self.assertRedirects(response, reverse('accounts:settings'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Alice')
        self.assertEqual(self.user.description, 'Hello there')

    def test_invalid_username_rejected_by_validator(self):
        bad_user = User(username='invalid username')
        with self.assertRaises(ValidationError):
            bad_user.full_clean()
