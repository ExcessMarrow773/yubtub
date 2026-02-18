from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


def isVMuted(username: str):
	user = get_object_or_404(User, username=username)
	return user.groups.filter(name='vMuted').exists()

def isPMuted(username: str):
	user = get_object_or_404(User, username=username)
	return user.groups.filter(name='pMuted').exists()

def isMuted(username: str):
	user = get_object_or_404(User, username=username)
	return user.groups.filter(name='Muted').exists()
