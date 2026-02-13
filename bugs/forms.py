from django import forms
from bugs.models import BugReport
from django.contrib.auth import get_user_model
User = get_user_model()

class BugReportForm(forms.ModelForm):
    class Meta:
        model = BugReport
        fields = ['title', 'body', 'type', 'github_issue']