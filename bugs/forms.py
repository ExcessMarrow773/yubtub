from django import forms
from bugs.models import BugReport
from django.contrib.auth import get_user_model
User = get_user_model()

class BugReportForm(forms.ModelForm):
    class Meta:
        model = BugReport
        fields = ['title', 'issues', 'description', 'type', 'github_issue']

        widgets = {
            'issues': forms.Textarea(attrs={'style': 'width: 400px; height: 140px;'}),
            'description': forms.Textarea(attrs={'style': 'width: 400px; height: 140px;'}),
        }