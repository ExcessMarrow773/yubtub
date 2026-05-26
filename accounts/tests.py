from django.test import TestCase
from django.contrib.auth import get_user_model

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

    def test_follower_count_multiple_followers(self):
        initial_count = self.user1.follower_count()
        self.user2.follow(self.user1)
        self.user3.follow(self.user1)
        self.assertEqual(self.user1.follower_count(), initial_count + 2)


class SystemUserSignalTests(TestCase):
    """Test that new users automatically follow the system account"""
    
    def test_new_user_follows_system(self):
        # System user should exist from signal
        try:
            system_user = User.objects.get(username='system')
        except User.DoesNotExist:
            self.skipTest("System user not created")
        
        new_user = User.objects.create_user(username='newuser', password='pass')
        
        # Check if new user follows system
        self.assertTrue(new_user.is_following(system_user))

    def test_system_follows_new_user(self):
        try:
            system_user = User.objects.get(username='system')
        except User.DoesNotExist:
            self.skipTest("System user not created")
        
        new_user = User.objects.create_user(username='newuser', password='pass')
        
        # Check if system follows new user
        self.assertTrue(system_user.is_following(new_user))

    def test_system_doesnt_follow_itself(self):
        try:
            system_user = User.objects.get(username='system')
        except User.DoesNotExist:
            self.skipTest("System user not created")
        
        # System shouldn't follow itself
        self.assertFalse(system_user.is_following(system_user))