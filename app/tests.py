from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

from app.models import Video, VideoComment, Post, PostComment

User = get_user_model()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_video(author_user, **kwargs):
    """Create a Video whose author field holds the user's PK (integer)."""
    defaults = dict(
        title='Test Video',
        video_file='videos/test.mp4',
        thumbnail='thumbnail/test.jpg',
    )
    defaults.update(kwargs)
    return Video.objects.create(author=author_user.pk, **defaults)


def make_post(author_user, **kwargs):
    """Create a Post whose author field holds the user's PK (integer)."""
    defaults = dict(title='Test Post', body='Test body')
    defaults.update(kwargs)
    return Post.objects.create(author=author_user.pk, **defaults)


# ---------------------------------------------------------------------------
# VideoComment mention tests
# ---------------------------------------------------------------------------

class VideoCommentMentionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob',   password='pass123')
        self.user3 = User.objects.create_user(username='charlie', password='pass123')
        self.video = make_video(self.user1)

    def _comment(self, body):
        return VideoComment.objects.create(
            author=self.user1.pk, body=body, video=self.video
        )

    def test_get_mentions_extracts_usernames(self):
        comment = self._comment('Hey @bob and @charlie, check this out!')
        self.assertEqual(set(comment.get_mentions()), {'bob', 'charlie'})

    def test_get_mentions_with_no_mentions(self):
        comment = self._comment('Just a regular comment')
        self.assertEqual(comment.get_mentions(), [])

    def test_get_valid_mentions_filters_non_existent_users(self):
        comment = self._comment('Hey @bob and @nonexistent!')
        self.assertEqual(comment.get_valid_mentions(), ['bob'])

    def test_get_valid_mentions_with_all_valid_users(self):
        comment = self._comment('Hey @bob and @charlie!')
        self.assertEqual(set(comment.get_valid_mentions()), {'bob', 'charlie'})

    def test_get_valid_mentions_with_duplicate_mentions(self):
        comment = self._comment('Hey @bob, @bob, listen @bob!')
        self.assertEqual(comment.get_valid_mentions().count('bob'), 1)

    def test_mentions_with_underscores_and_numbers(self):
        User.objects.create_user(username='user_123', password='pass')
        comment = self._comment('Hey @user_123!')
        self.assertIn('user_123', comment.get_mentions())
        self.assertIn('user_123', comment.get_valid_mentions())


# ---------------------------------------------------------------------------
# PostComment mention tests
# ---------------------------------------------------------------------------

class PostCommentMentionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice',   password='pass123')
        self.user2 = User.objects.create_user(username='bob',     password='pass123')
        self.user3 = User.objects.create_user(username='charlie', password='pass123')
        self.post = make_post(self.user1)

    def _comment(self, body):
        return PostComment.objects.create(
            author=self.user1.pk, body=body, post=self.post
        )

    def test_get_mentions_extracts_usernames(self):
        comment = self._comment('Hey @bob and @charlie, check this out!')
        self.assertEqual(set(comment.get_mentions()), {'bob', 'charlie'})

    def test_get_mentions_with_no_mentions(self):
        comment = self._comment('Just a regular comment')
        self.assertEqual(comment.get_mentions(), [])

    def test_get_valid_mentions_filters_non_existent_users(self):
        comment = self._comment('Hey @bob and @nonexistent!')
        self.assertEqual(comment.get_valid_mentions(), ['bob'])

    def test_get_valid_mentions_with_all_valid_users(self):
        comment = self._comment('Hey @bob and @charlie!')
        self.assertEqual(set(comment.get_valid_mentions()), {'bob', 'charlie'})

    def test_mentions_in_middle_of_text(self):
        comment = self._comment('I think @bob should talk to @charlie about this.')
        self.assertEqual(set(comment.get_mentions()), {'bob', 'charlie'})

    def test_mentions_at_end_of_sentence(self):
        comment = self._comment('Great work @bob!')
        self.assertEqual(comment.get_mentions(), ['bob'])


# ---------------------------------------------------------------------------
# Video thumbnail tests
# ---------------------------------------------------------------------------

class VideoThumbnailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_video_without_thumbnail_does_not_raise(self):
        # generate_thumbnail will fail silently in tests (no real file)
        video = Video.objects.create(
            author=self.user.pk,
            title='No Thumbnail',
            video_file='videos/test.mp4',
        )
        self.assertIsNotNone(video.pk)

    def test_video_with_thumbnail_keeps_it(self):
        video = Video.objects.create(
            author=self.user.pk,
            title='Has Thumbnail',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/existing.jpg',
        )
        original = video.thumbnail.name
        video.save()
        self.assertEqual(video.thumbnail.name, original)


# ---------------------------------------------------------------------------
# Video like tests
# ---------------------------------------------------------------------------

class VideoLikeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob',   password='pass123')
        self.video = make_video(self.user1)

    def _like(self):
        return self.client.post(
            reverse('app:like-video'),
            data=f'{{"video_id": {self.video.id}}}',
            content_type='application/json',
        )

    def test_like_video_increments_likes(self):
        self.client.login(username='alice', password='pass123')
        initial = self.video.likes
        self._like()
        self.video.refresh_from_db()
        self.assertEqual(self.video.likes, initial + 1)

    def test_user_added_to_liked_users(self):
        self.client.login(username='alice', password='pass123')
        self._like()
        self.video.refresh_from_db()
        self.assertIn(self.user1, self.video.likedUsers.all())

    def test_unlike_removes_user_from_liked_users(self):
        self.client.login(username='alice', password='pass123')
        self.video.likedUsers.add(self.user1)
        self.video.likes = 1
        self.video.save()
        self._like()
        self.video.refresh_from_db()
        self.assertNotIn(self.user1, self.video.likedUsers.all())

    def test_like_requires_login(self):
        response = self._like()
        self.assertEqual(response.status_code, 403)


# ---------------------------------------------------------------------------
# Video view-count tests
# ---------------------------------------------------------------------------

class VideoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user  = User.objects.create_user(username='alice', password='pass123')
        self.video = make_video(self.user)

    def test_viewing_video_increments_views_once(self):
        self.client.login(username='alice', password='pass123')
        initial = self.video.views

        self.client.get(reverse('app:watch', args=[self.video.pk]))
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, initial + 1)

        # Second visit by same user should NOT increment
        self.client.get(reverse('app:watch', args=[self.video.pk]))
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, initial + 1)

    def test_user_added_to_viewed_users(self):
        self.client.login(username='alice', password='pass123')
        self.client.get(reverse('app:watch', args=[self.video.pk]))
        self.video.refresh_from_db()
        self.assertIn(self.user, self.video.viewedUsers.all())


# ---------------------------------------------------------------------------
# Following-page tests
# ---------------------------------------------------------------------------

class FollowingPageTests(TestCase):
    def setUp(self):
        self.client  = Client()
        self.user1   = User.objects.create_user(username='alice',   password='pass123')
        self.user2   = User.objects.create_user(username='bob',     password='pass123')
        self.user3   = User.objects.create_user(username='charlie', password='pass123')

    def test_following_page_accessible_when_logged_in(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('app:following'))
        self.assertEqual(response.status_code, 200)

    def test_following_page_shows_followed_user_content(self):
        self.client.login(username='alice', password='pass123')
        self.user1.follow(self.user2)

        make_post(self.user2, title='Bob Post')

        response = self.client.get(reverse('app:following'))
        self.assertContains(response, 'Bob Post')

    def test_following_page_does_not_show_unfollowed_content(self):
        self.client.login(username='alice', password='pass123')
        # Alice does NOT follow charlie
        make_post(self.user3, title='Charlie Post')

        response = self.client.get(reverse('app:following'))
        self.assertNotContains(response, 'Charlie Post')

    def test_following_page_requires_login(self):
        response = self.client.get(reverse('app:following'))
        # Should redirect to login
        self.assertIn(response.status_code, [302, 404])


# ---------------------------------------------------------------------------
# Account-page tests
# ---------------------------------------------------------------------------

class AccountPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1  = User.objects.create_user(username='alice', password='pass123')
        self.user2  = User.objects.create_user(username='bob',   password='pass123')

    def test_account_page_shows_user_content_sorted(self):
        self.client.login(username='alice', password='pass123')

        video = make_video(self.user1, title='Video')
        post  = make_post(self.user1,  title='Post')

        response = self.client.get(reverse('app:account', args=[self.user1.pk]))
        combined = response.context['combined']
        # Verify descending date order
        for i in range(len(combined) - 1):
            self.assertGreaterEqual(combined[i].created_on, combined[i + 1].created_on)

    def test_account_page_shows_follow_button_for_other_users(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('app:account', args=[self.user2.pk]))
        self.assertContains(response, 'id="follow-button"')
        self.assertFalse(response.context['isUsersAccount'])

    def test_account_page_no_follow_button_for_own_account(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('app:account', args=[self.user1.pk]))
        self.assertNotContains(response, 'id="follow-button"')
        self.assertTrue(response.context['isUsersAccount'])


# ---------------------------------------------------------------------------
# Index-page tests
# ---------------------------------------------------------------------------

class IndexPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1  = User.objects.create_user(username='alice', password='pass123')
        self.user2  = User.objects.create_user(username='bob',   password='pass123')

    def test_index_combines_videos_and_posts(self):
        make_video(self.user1, title='Video 1')
        make_post(self.user2,  title='Post 1')

        response = self.client.get(reverse('app:index'))
        combined = response.context['combined']
        self.assertEqual(len(combined), 2)
        types = {item.type for item in combined}
        self.assertIn('video', types)
        self.assertIn('post',  types)

    def test_index_sorts_by_created_on_descending(self):
        old_video = make_video(self.user1, title='Old Video')
        # Manually backdate the old video
        Video.objects.filter(pk=old_video.pk).update(
            created_on=timezone.now() - timedelta(days=2)
        )
        make_post(self.user2, title='New Post')

        response = self.client.get(reverse('app:index'))
        combined = response.context['combined']
        self.assertEqual(combined[0].type, 'post')
        self.assertEqual(combined[1].type, 'video')


# ---------------------------------------------------------------------------
# Markdown-filter tests
# ---------------------------------------------------------------------------

class MarkdownFilterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username='alice', password='pass123')
        self.post   = make_post(
            self.user,
            title='Test Post',
            body='# Header\n\n**Bold text**',
        )

    def test_post_renders_markdown(self):
        response = self.client.get(reverse('app:post', args=[self.post.pk]))
        self.assertContains(response, '<h1>Header</h1>')
        self.assertContains(response, '<strong>Bold text</strong>')


# ---------------------------------------------------------------------------
# URL pattern smoke tests
# ---------------------------------------------------------------------------

class URLPatternTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username='alice', password='pass123')

    def test_index_url(self):
        self.assertEqual(self.client.get(reverse('app:index')).status_code, 200)

    def test_login_url(self):
        self.assertEqual(self.client.get(reverse('app:login')).status_code, 200)

    def test_register_url(self):
        self.assertEqual(self.client.get(reverse('app:register')).status_code, 200)

    def test_todo_url(self):
        self.assertEqual(self.client.get(reverse('app:TODO')).status_code, 200)

    def test_cornhub_url(self):
        self.assertEqual(self.client.get(reverse('app:cornhub')).status_code, 200)

    def test_mdhelp_url(self):
        self.assertEqual(self.client.get(reverse('app:mdHelp')).status_code, 200)


# ---------------------------------------------------------------------------
# Empty description tests
# ---------------------------------------------------------------------------

class EmptyDescriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')

    def _video(self, description):
        return Video.objects.create(
            author=self.user.pk,
            title='Test',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            description=description,
        )

    def test_empty_description_gets_default(self):
        v = self._video('')
        v.refresh_from_db()
        self.assertEqual(v.description, "There was no description provided for this video")

    def test_none_description_gets_default(self):
        v = self._video(None)
        v.refresh_from_db()
        self.assertEqual(v.description, "There was no description provided for this video")

    def test_whitespace_description_gets_default(self):
        v = self._video('   ')
        v.refresh_from_db()
        self.assertEqual(v.description, "There was no description provided for this video")

    def test_real_description_is_preserved(self):
        v = self._video('A real description.')
        v.refresh_from_db()
        self.assertEqual(v.description, 'A real description.')


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------

class SearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username='alice', password='pass123')
        make_video(self.user, title='Cooking With Fire', description='flames and heat')
        make_post(self.user,  title='Travel Blog',       body='explored the mountains')

    def test_search_returns_matching_video(self):
        response = self.client.get(reverse('app:search') + '?q=Cooking')
        combined = response.context['combined']
        titles = [c.title for c in combined]
        self.assertIn('Cooking With Fire', titles)

    def test_search_returns_matching_post(self):
        response = self.client.get(reverse('app:search') + '?q=Travel')
        combined = response.context['combined']
        titles = [c.title for c in combined]
        self.assertIn('Travel Blog', titles)

    def test_search_empty_query_returns_all(self):
        response = self.client.get(reverse('app:search') + '?q=')
        combined = response.context['combined']
        self.assertEqual(len(combined), 2)

    def test_search_no_results(self):
        response = self.client.get(reverse('app:search') + '?q=zzznomatch')
        combined = response.context['combined']
        self.assertEqual(len(combined), 0)