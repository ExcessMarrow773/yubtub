from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from .models import Video, Post, VideoComment, PostComment


class VideoModelTests(TestCase):
	def test_str_returns_title(self):
		v = Video.objects.create(
			title='My Video',
			video_file='videos/fake.mp4',
			thumbnail='thumbnail/fake.jpg',
			description='a description',
		)
		self.assertEqual(str(v), 'My Video')

	def test_was_published_recently_true(self):
		v = Video.objects.create(
			title='Recent',
			video_file='videos/fake.mp4',
			thumbnail='thumbnail/fake.jpg',
			description='desc',
		)
		self.assertTrue(v.was_published_recently())

	def test_was_published_recently_false_for_old_video(self):
		v = Video.objects.create(
			title='Old',
			video_file='videos/fake.mp4',
			thumbnail='thumbnail/fake.jpg',
			description='desc',
		)
		v.created_on = timezone.now() - timedelta(days=2)
		v.save(update_fields=['created_on'])
		self.assertFalse(v.was_published_recently())


class PostModelTests(TestCase):
	def test_str_returns_title(self):
		p = Post.objects.create(title='A Post', body='body', author='bob')
		self.assertEqual(str(p), 'A Post')

	def test_was_published_recently(self):
		p = Post.objects.create(title='Recent Post', body='b', author='bob')
		self.assertTrue(p.was_published_recently())


class CommentModelTests(TestCase):
	def test_video_comment_and_post_comment_str(self):
		v = Video.objects.create(
			title='C',
			video_file='videos/fake.mp4',
			thumbnail='thumbnail/fake.jpg',
			description='d',
		)
		vc = VideoComment.objects.create(author='alice', body='nice', video=v)
		self.assertEqual(str(vc), 'alice')

		p = Post.objects.create(title='P', body='b', author='bob')
		pc = PostComment.objects.create(author='charlie', body='ok', post=p)
		self.assertEqual(str(pc), 'charlie')
