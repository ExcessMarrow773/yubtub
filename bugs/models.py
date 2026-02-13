from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
TYPE_CHOICES = {
    'BUG': 'Bug',
    'DOCS': 'Documentation',
    'NEW': 'Enhancement',
    'HUH?': 'Question',
}

class BugReport(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now=True, auto_now_add=False)
    type = models.CharField(choices=TYPE_CHOICES, max_length=50, default='BUG')
    github_issue = models.CharField(max_length=100, blank=True, null=True)
    has_github_issue = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title