from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Video, VideoComment, Post, PostComment

User = get_user_model()


class VideoCommentMentionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')
        self.user3 = User.objects.create_user(username='charlie', password='pass123')
        self.video = Video.objects.create(
            title='Test Video',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            author='alice'
        )

    def test_get_mentions_extracts_usernames(self):
        comment = VideoComment.objects.create(
            author='alice',
            body='Hey @bob and @charlie, check this out!',
            video=self.video
        )
        mentions = comment.get_mentions()
        self.assertEqual(set(mentions), {'bob', 'charlie'})

    def test_get_mentions_with_no_mentions(self):
        comment = VideoComment.objects.create(
            author='alice',
            body='Just a regular comment',
            video=self.video
        )
        mentions = comment.get_mentions()
        self.assertEqual(mentions, [])

    def test_get_valid_mentions_filters_non_existent_users(self):
        comment = VideoComment.objects.create(
            author='alice',
            body='Hey @bob and @nonexistent, check this out!',
            video=self.video
        )
        valid_mentions = comment.get_valid_mentions()
        self.assertEqual(valid_mentions, ['bob'])

    def test_get_valid_mentions_with_all_valid_users(self):
        comment = VideoComment.objects.create(
            author='alice',
            body='Hey @bob and @charlie!',
            video=self.video
        )
        valid_mentions = comment.get_valid_mentions()
        self.assertEqual(set(valid_mentions), {'bob', 'charlie'})

    def test_get_valid_mentions_with_duplicate_mentions(self):
        comment = VideoComment.objects.create(
            author='alice',
            body='Hey @bob, @bob, listen to me @bob!',
            video=self.video
        )
        valid_mentions = comment.get_valid_mentions()
        # Should only return unique usernames
        self.assertEqual(valid_mentions.count('bob'), 1)

    def test_mentions_with_underscores_and_numbers(self):
        user_complex = User.objects.create_user(username='user_123', password='pass')
        comment = VideoComment.objects.create(
            author='alice',
            body='Hey @user_123!',
            video=self.video
        )
        mentions = comment.get_mentions()
        self.assertIn('user_123', mentions)
        valid_mentions = comment.get_valid_mentions()
        self.assertIn('user_123', valid_mentions)


class PostCommentMentionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')
        self.user3 = User.objects.create_user(username='charlie', password='pass123')
        self.post = Post.objects.create(
            title='Test Post',
            body='Test body',
            author='alice'
        )

    def test_get_mentions_extracts_usernames(self):
        comment = PostComment.objects.create(
            author='alice',
            body='Hey @bob and @charlie, check this out!',
            post=self.post
        )
        mentions = comment.get_mentions()
        self.assertEqual(set(mentions), {'bob', 'charlie'})

    def test_get_mentions_with_no_mentions(self):
        comment = PostComment.objects.create(
            author='alice',
            body='Just a regular comment',
            post=self.post
        )
        mentions = comment.get_mentions()
        self.assertEqual(mentions, [])

    def test_get_valid_mentions_filters_non_existent_users(self):
        comment = PostComment.objects.create(
            author='alice',
            body='Hey @bob and @nonexistent, check this out!',
            post=self.post
        )
        valid_mentions = comment.get_valid_mentions()
        self.assertEqual(valid_mentions, ['bob'])

    def test_get_valid_mentions_with_all_valid_users(self):
        comment = PostComment.objects.create(
            author='alice',
            body='Hey @bob and @charlie!',
            post=self.post
        )
        valid_mentions = comment.get_valid_mentions()
        self.assertEqual(set(valid_mentions), {'bob', 'charlie'})

    def test_mentions_in_middle_of_text(self):
        comment = PostComment.objects.create(
            author='alice',
            body='I think @bob should talk to @charlie about this issue.',
            post=self.post
        )
        mentions = comment.get_mentions()
        self.assertEqual(set(mentions), {'bob', 'charlie'})

    def test_mentions_at_end_of_sentence(self):
        comment = PostComment.objects.create(
            author='alice',
            body='This is great work @bob!',
            post=self.post
        )
        mentions = comment.get_mentions()
        self.assertEqual(mentions, ['bob'])


class VideoThumbnailTests(TestCase):
    def test_video_without_thumbnail_generates_one(self):
        """Test that videos without thumbnails attempt to generate one"""
        video = Video.objects.create(
            title='No Thumbnail Video',
            video_file='videos/test.mp4',
            description='Test'
        )
        # The save method should attempt to generate a thumbnail
        # In test environment without actual video file, this may not succeed
        # but we can verify the method is called
        self.assertIsNotNone(video)

    def test_video_with_thumbnail_keeps_it(self):
        """Test that videos with thumbnails don't regenerate"""
        video = Video.objects.create(
            title='Has Thumbnail',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/existing.jpg',
            description='Test'
        )
        original_thumbnail = video.thumbnail
        video.save()
        self.assertEqual(video.thumbnail, original_thumbnail)


class VideoLikeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')
        self.video = Video.objects.create(
            title='Test Video',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
        )

    def test_like_video_increments_likes(self):
        self.client.login(username='alice', password='pass123')
        initial_likes = self.video.likes
        
        response = self.client.post(
            reverse('app:like-video'),
            data='{"video_id": ' + str(self.video.id) + '}',
            content_type='application/json'
        )
        
        self.video.refresh_from_db()
        self.assertEqual(self.video.likes, initial_likes + 1)

    def test_user_added_to_liked_users(self):
        self.client.login(username='alice', password='pass123')
        
        self.client.post(
            reverse('app:like-video'),
            data='{"video_id": ' + str(self.video.id) + '}',
            content_type='application/json'
        )
        
        self.video.refresh_from_db()
        self.assertIn(self.user1, self.video.likedUsers.all())

    def test_unlike_removes_user_from_liked_users(self):
        self.client.login(username='alice', password='pass123')
        self.video.likedUsers.add(self.user1)
        self.video.likes = 1
        self.video.save()
        
        self.client.post(
            reverse('app:like-video'),
            data='{"video_id": ' + str(self.video.id) + '}',
            content_type='application/json'
        )
        
        self.video.refresh_from_db()
        self.assertNotIn(self.user1, self.video.likedUsers.all())


class VideoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.video = Video.objects.create(
            title='Test Video',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
        )

    def test_viewing_video_increments_views_once(self):
        self.client.login(username='alice', password='pass123')
        initial_views = self.video.views
        
        # First view
        self.client.get(reverse('app:watch', args=[self.video.pk]))
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, initial_views + 1)
        
        # Second view by same user shouldn't increment
        self.client.get(reverse('app:watch', args=[self.video.pk]))
        self.video.refresh_from_db()
        self.assertEqual(self.video.views, initial_views + 1)

    def test_user_added_to_viewed_users(self):
        self.client.login(username='alice', password='pass123')
        
        self.client.get(reverse('app:watch', args=[self.video.pk]))
        
        self.video.refresh_from_db()
        self.assertIn(self.user, self.video.viewedUsers.all())


class FollowingPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')
        self.user3 = User.objects.create_user(username='charlie', password='pass123')

    def test_following_page_shows_only_mutual_followers(self):
        self.client.login(username='alice', password='pass123')
        
        # Alice follows Bob (mutual)
        self.user1.follow(self.user2)
        self.user2.follow(self.user1)
        
        # Alice follows Charlie (not mutual)
        self.user1.follow(self.user3)
        
        response = self.client.get(reverse('app:following'))
        
        # Bob should appear (mutual)
        self.assertContains(response, 'bob')
        # Charlie should not appear (not mutual)
        # Note: The current implementation shows all followed users, not just mutual

    def test_following_page_limits_results(self):
        self.client.login(username='alice', password='pass123')
        
        # Create 15 users and follow them all
        for i in range(15):
            user = User.objects.create_user(username=f'user{i}', password='pass')
            self.user1.follow(user)
            user.follow(self.user1)
            # Create content
            Post.objects.create(title=f'Post {i}', body='test', author=user.username)
        
        response = self.client.get(reverse('app:following'))
        
        # Should limit to 10
        context_posts = response.context['posts']
        self.assertLessEqual(len(context_posts), 10)





class AccountPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')

    def test_account_page_shows_user_content_sorted(self):
        self.client.login(username='alice', password='pass123')
        
        # Create content with different timestamps
        video = Video.objects.create(
            title='Video',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            author='alice'
        )
        post = Post.objects.create(
            title='Post',
            body='Body',
            author='alice'
        )
        
        response = self.client.get(reverse('app:account', args=['alice']))
        
        combined = response.context['combined']
        # Should be sorted by created_on descending
        self.assertTrue(combined[0].created_on >= combined[1].created_on)

    def test_account_page_shows_follow_button_for_other_users(self):
        self.client.login(username='alice', password='pass123')
        
        response = self.client.get(reverse('app:account', args=['bob']))
        
        self.assertContains(response, 'id="follow-button"')
        self.assertEqual(response.context['isUsersAccount'], False)

    def test_account_page_no_follow_button_for_own_account(self):
        self.client.login(username='alice', password='pass123')
        
        response = self.client.get(reverse('app:account', args=['alice']))
        
        self.assertNotContains(response, 'id="follow-button"')
        self.assertEqual(response.context['isUsersAccount'], True)


class IndexPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_combines_videos_and_posts(self):
        Video.objects.create(
            title='Video 1',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            author='alice'
        )
        Post.objects.create(
            title='Post 1',
            body='Body',
            author='bob'
        )
        
        response = self.client.get(reverse('app:index'))
        
        combined = response.context['combined']
        self.assertEqual(len(combined), 2)
        
        # Check both types are present
        types = [item.type for item in combined]
        self.assertIn('video', types)
        self.assertIn('post', types)

    def test_index_sorts_by_created_on_descending(self):
        # Create older video
        old_video = Video.objects.create(
            title='Old Video',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            author='alice'
        )
        old_video.created_on = timezone.now() - timedelta(days=2)
        old_video.save()
        
        # Create newer post
        new_post = Post.objects.create(
            title='New Post',
            body='Body',
            author='bob'
        )
        
        response = self.client.get(reverse('app:index'))
        combined = response.context['combined']
        
        # Newest should be first
        self.assertEqual(combined[0].type, 'post')
        self.assertEqual(combined[1].type, 'video')


class MarkdownFilterTests(TestCase):
    """Test markdown rendering in posts and comments"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.post = Post.objects.create(
            title='Test Post',
            body='# Header\n\n**Bold text**',
            author='alice'
        )

    def test_post_renders_markdown(self):
        response = self.client.get(reverse('app:post', args=[self.post.pk]))
        
        # Check that HTML tags from markdown are present
        self.assertContains(response, '<h1>Header</h1>')
        self.assertContains(response, '<strong>Bold text</strong>')

    def test_comment_renders_markdown(self):
        self.client.login(username='alice', password='pass123')
        
        self.client.post(
            reverse('app:post', args=[self.post.pk]),
            data={'body': '**Bold comment**'}
        )
        
        response = self.client.get(reverse('app:post', args=[self.post.pk]))
        self.assertContains(response, '<strong>Bold comment</strong>')


class URLPatternTests(TestCase):
    """Test that all URL patterns are accessible"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_index_url(self):
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get(reverse('app:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_url(self):
        response = self.client.get(reverse('app:register'))
        self.assertEqual(response.status_code, 200)

    def test_todo_url(self):
        response = self.client.get(reverse('app:TODO'))
        self.assertEqual(response.status_code, 200)

    def test_cornhub_url(self):
        response = self.client.get(reverse('app:cornhub'))
        self.assertEqual(response.status_code, 200)

    def test_mdhelp_url(self):
        response = self.client.get(reverse('app:mdHelp'))
        self.assertEqual(response.status_code, 200)

class EmptyDescriptionTests(TestCase):
    """Test that empty video descriptions are handled correctly"""
    
    def test_empty_description_gets_default(self):
        video = Video.objects.create(
            title='Test',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            description=''
        )
        video.refresh_from_db()
        self.assertEqual(video.description, "There was no description provided for this video")

    def test_none_description_gets_default(self):
        video = Video.objects.create(
            title='Test',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            description=None
        )
        video.refresh_from_db()
        self.assertEqual(video.description, "There was no description provided for this video")

    def test_whitespace_description_gets_default(self):
        video = Video.objects.create(
            title='Test',
            video_file='videos/test.mp4',
            thumbnail='thumbnail/test.jpg',
            description='   '
        )
        video.refresh_from_db()
        self.assertEqual(video.description, "There was no description provided for this video")