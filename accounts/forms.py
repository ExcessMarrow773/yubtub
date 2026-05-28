from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils import timezone
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

User = get_user_model()

class ProfileDetailsChange(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'use_naughty_words', 'description', 'email', 'profile_pic']

class ProfileUsernameChange(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

class ProfilePasswordChange(PasswordChangeForm):
    user = User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

class CustomAuthenticationForm(AuthenticationForm):
    pass