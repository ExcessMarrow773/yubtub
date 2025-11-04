from django.test import TestCase

from django.contrib.auth import get_user_model

User = get_user_model()


class FollowTests(TestCase):
	def setUp(self):
		self.alice = User.objects.create_user(username='alice', password='pass')
		self.bob = User.objects.create_user(username='bob', password='pass')

	def test_follow_and_unfollow(self):
		# initially not following (except system user due to signal)
		self.assertFalse(self.alice.is_following(self.bob))

		# follow
		self.alice.follow(self.bob)
		self.assertTrue(self.alice.is_following(self.bob))
		self.assertTrue(self.bob.is_followed_by(self.alice))

		# follower count on bob should be 2 (alice + system from signal)
		self.assertEqual(self.bob.follower_count(), 2)

		# unfollow
		self.alice.unfollow(self.bob)
		self.assertFalse(self.alice.is_following(self.bob))
		# back to 1 (just system)
		self.assertEqual(self.bob.follower_count(), 1)

	def test_follow_self_is_allowed_but_idempotent(self):
		# following self should not error and should be idempotent
		self.alice.follow(self.alice)
		self.assertTrue(self.alice.is_following(self.alice))
		# calling follow again shouldn't duplicate
		self.alice.follow(self.alice)
		# Count is 2: system user + self
		self.assertEqual(self.alice.follower_count(), 2)