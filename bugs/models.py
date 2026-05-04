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
    issues = models.TextField(null=True)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now=True, auto_now_add=False)
    type = models.CharField(choices=TYPE_CHOICES, max_length=50, default='BUG')
    github_issue = models.CharField(max_length=100, blank=True, null=True)
    has_github_issue = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        first_save_kwargs = kwargs.copy()
        issueList = self.issues.split("\n")
        # First save to create the row and get a primary key (if new)
        super().save(*args, **kwargs)
        for i in issueList:
            BugIssues.objects.create(bug=self, issue=i)
    
class BugIssues(models.Model):
    bug = models.ForeignKey("bugs.BugReport", on_delete=models.CASCADE)
    issue = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
