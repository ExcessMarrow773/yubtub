import json

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import BugReport

User = get_user_model()


def json_body(bug_id):
    return json.dumps({'bug': bug_id})


class BugReportValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username='alice', password='pass123')

    def test_bug_report_submission_with_github_issue(self):
        self.client.login(username='alice', password='pass123')
        self.client.post(
            reverse('bugs:bugReport'),
            data={
                'title':        'Bug with login',
                'body':         'Cannot login sometimes',
                'type':         'BUG',
                'github_issue': 'https://github.com/user/repo/issues/1',
            },
        )
        bug = BugReport.objects.first()
        self.assertIsNotNone(bug)
        self.assertEqual(bug.github_issue, 'https://github.com/user/repo/issues/1')
        self.assertTrue(bug.has_github_issue)

    def test_bug_report_submission_without_github_issue(self):
        self.client.login(username='alice', password='pass123')
        self.client.post(
            reverse('bugs:bugReport'),
            data={'title': 'Simple bug', 'body': 'it breaks', 'type': 'BUG', 'github_issue': ''},
        )
        bug = BugReport.objects.first()
        self.assertIsNotNone(bug)
        self.assertFalse(bug.has_github_issue)

    def test_bug_report_type_choices(self):
        for choice_key in ['BUG', 'DOCS', 'NEW', 'HUH?']:
            BugReport.objects.create(
                title=f'Test {choice_key}',
                body='Test',
                type=choice_key,
                author=self.user.pk,
            )
        self.assertEqual(BugReport.objects.count(), 4)

    def test_bug_report_default_resolved_false(self):
        bug = BugReport.objects.create(
            title='Unresolved', body='x', type='BUG', author=self.user.pk
        )
        self.assertFalse(bug.resolved)

    def test_bug_str(self):
        bug = BugReport.objects.create(
            title='My Bug Report', body='details', type='BUG', author=self.user.pk
        )
        self.assertEqual(str(bug), 'My Bug Report')

    def test_resolve_bug_api(self):
        self.client.login(username='alice', password='pass123')
        bug = BugReport.objects.create(
            title='Resolve Me', body='x', type='BUG', author=self.user.pk
        )
        response = self.client.post(
            reverse('bugs:resolveBug'),
            data=json_body(bug.id),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        bug.refresh_from_db()
        self.assertTrue(bug.resolved)

    def test_resolve_bug_toggles_back(self):
        self.client.login(username='alice', password='pass123')
        bug = BugReport.objects.create(
            title='Toggle', body='x', type='BUG', author=self.user.pk, resolved=True
        )
        self.client.post(
            reverse('bugs:resolveBug'),
            data=json_body(bug.id),
            content_type='application/json',
        )
        bug.refresh_from_db()
        self.assertFalse(bug.resolved)

    def test_resolve_requires_login(self):
        bug = BugReport.objects.create(
            title='Auth Test', body='x', type='BUG', author=self.user.pk
        )
        response = self.client.post(
            reverse('bugs:resolveBug'),
            data=json_body(bug.id),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_resolve_invalid_json(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.post(
            reverse('bugs:resolveBug'),
            data='not json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class URLPatternTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user   = User.objects.create_user(username='alice', password='pass123')

    def test_bug_report_url(self):
        self.assertEqual(self.client.get(reverse('bugs:bugReport')).status_code, 200)

    def test_bug_report_index_url(self):
        self.assertEqual(self.client.get(reverse('bugs:bugReportIndex')).status_code, 200)

    def test_bug_view_url(self):
        bug = BugReport.objects.create(
            title='View Me', body='test', type='BUG', author=self.user.pk
        )
        self.assertEqual(
            self.client.get(reverse('bugs:bugView', args=[bug.pk])).status_code, 200
        )

    def test_bug_view_404_for_missing_bug(self):
        self.assertEqual(
            self.client.get(reverse('bugs:bugView', args=[99999])).status_code, 404
        )