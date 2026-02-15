from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import BugReport

User = get_user_model()
# Create your tests here.

class BugReportValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_bug_report_with_github_issue(self):
        self.client.login(username='alice', password='pass123')
        
        response = self.client.post(
            reverse('bugs:bugReport'),
            data={
                'title': 'Bug with login',
                'body': 'Cannot login sometimes',
                'type': 'BUG',
                'github_issue': 'https://github.com/user/repo/issues/1',
            }
        )
        
        bug = BugReport.objects.first()
        self.assertIsNotNone(bug)
        self.assertEqual(bug.github_issue, 'https://github.com/user/repo/issues/1')
        self.assertTrue(bug.has_github_issue)

    def test_bug_report_type_choices(self):
        for choice_key in ['BUG', 'DOCS', 'NEW', 'HUH?']:
            BugReport.objects.create(
                title=f'Test {choice_key}',
                body='Test',
                type=choice_key,
                author='alice'
            )
        
        self.assertEqual(BugReport.objects.count(), 4)

class URLPatternTests(TestCase):
    """Test that all URL patterns are accessible"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass123')

    def test_bug_report_url(self):
        response = self.client.get(reverse('bugs:bugReport'))
        self.assertEqual(response.status_code, 200)
    
    def test_bug_report_index_url(self):
        response = self.client.get(reverse('bugs:bugReportIndex'))
        self.assertEqual(response.status_code, 200)

#    def test_bug_report_view_url(self):
#        response = self.client.get(reverse('bugs:bugView'))
#        self.assertEqual(response.status_code, 200)