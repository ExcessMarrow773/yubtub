from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from .models import Video, VideoComment, Post, PostComment, BugReport


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

	def test_description_defaults_when_empty(self):
		v = Video.objects.create(
			title='No Desc',
			video_file='videos/fake.mp4',
			thumbnail='thumbnail/fake.jpg',
			description='',
		)
		# Reload from DB to ensure save() side-effects are observed
		v.refresh_from_db()
		self.assertEqual(v.description, "There was no description provided for this video")

class VideoCommentModelTests(TestCase):
    def test_str_returns_author(self):
        v = Video.objects.create(
            title='C',
            video_file='videos/fake.mp4',
            thumbnail='thumbnail/fake.jpg',
            description='d',
        )
        vc = VideoComment.objects.create(author='commenter', body='nice', video=v)
        self.assertEqual(str(vc), 'commenter')


class PostModelTests(TestCase):
    def test_str_returns_title(self):
        p = Post.objects.create(title='Post Title', body='body text')
        self.assertEqual(str(p), 'Post Title')

    def test_was_published_recently_true(self):
        p = Post.objects.create(title='Recent Post', body='x')
        self.assertTrue(p.was_published_recently())

    def test_was_published_recently_false_for_old_post(self):
        p = Post.objects.create(title='Old Post', body='x')
        p.created_on = timezone.now() - timedelta(days=2)
        p.save(update_fields=['created_on'])
        self.assertFalse(p.was_published_recently())


class PostCommentModelTests(TestCase):
    def test_str_returns_author(self):
        p = Post.objects.create(title='Post for Comment', body='b')
        pc = PostComment.objects.create(author='poster', body='hi', post=p)
        self.assertEqual(str(pc), 'poster')


class BugReportModelTests(TestCase):
    def test_str_returns_title(self):
        b = BugReport.objects.create(title='Bug 1', body='details')
        self.assertEqual(str(b), 'Bug 1')

    def test_has_github_issue_default_false(self):
        b = BugReport.objects.create(title='Bug 2', body='d', github_issue='')
        self.assertFalse(b.has_github_issue)

    def test_github_issue_field_does_not_auto_set_flag(self):
        # model does not auto-toggle has_github_issue; view sets it.
        b = BugReport.objects.create(title='Bug 3', body='d', github_issue='http://example.com/issue/1')
        self.assertFalse(b.has_github_issue)

    def test_can_set_has_github_issue_true(self):
        b = BugReport.objects.create(title='Bug 4', body='d', github_issue='http://x', has_github_issue=True)
        self.assertTrue(b.has_github_issue)
