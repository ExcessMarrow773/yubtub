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
	issueModel = models.ManyToManyField("bugs.BugIssue", blank=True)
	description = models.TextField()
	created_on = models.DateTimeField(auto_now=True, auto_now_add=False)
	type = models.CharField(choices=TYPE_CHOICES, max_length=50, default='BUG')
	github_issue = models.CharField(max_length=100, blank=True, null=True)
	has_github_issue = models.BooleanField(default=False)
	resolved = models.BooleanField(default=False)

	def __str__(self):
		return self.title


	def save(self, *args, **kwargs):        
		old_issues = set(self.issueModel.all())
		print(list(self.issueModel.all()))
		super().save(*args, **kwargs)
		
		if self.issues:
			new_issues = set(
				i.strip() for i in self.issues.split("\n") if i.strip()
			)
			
			# Delete issues that were removed from the text
			removed = old_issues - new_issues
			self.issueModel.filter(issue__in=removed).delete()
			
			# Only create issues that don't already exist
			to_create = new_issues - old_issues
			for issue_text in to_create:
				issue = BugIssue.objects.create(bug=self, issue=issue_text)
				self.issueModel.add(issue)
		print(old_issues)
		print(new_issues)



class BugIssue(models.Model):
	bug = models.ForeignKey("bugs.BugReport", on_delete=models.CASCADE)
	issue = models.TextField()
	resolved = models.BooleanField(default=False)

	def __str__(self):
		if self.resolved==True:
				return f"{self.issue} [x]"
		else:
				return f"{self.issue} [_]"
