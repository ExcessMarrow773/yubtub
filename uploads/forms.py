from django import forms
from django.utils import timezone
from uploads.models import Upload
from django.contrib.auth import get_user_model

User = get_user_model()

class UploadFileForm(forms.ModelForm):
	class Meta:
		model = Upload
		fields = ['name', 'file']