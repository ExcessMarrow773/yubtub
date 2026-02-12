from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils import timezone
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

class CustomAuthenticationForm(AuthenticationForm):
    pass

class ProfileDetailsChange(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image', 'first_name', 'last_name', 'email']

class ProfileUsernameChange(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class ProfilePasswordChange(PasswordChangeForm):
    user = User
