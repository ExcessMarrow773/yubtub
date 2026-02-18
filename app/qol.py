from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

def isVMuted(request):
	if not request.is_authenticated:
		return False
	username = request.user.username

	user = User.objects.get(username=username)
	return user.groups.filter(name='vMuted').exists()

def isPMuted(request):
	if not request.is_authenticated:
		return False
	username = request.user.username

	user = User.objects.get(username=username)
	return user.groups.filter(name='pMuted').exists()

def isMuted(request):
	if not request.is_authenticated:
		return False

	username = request.user.username

	user = User.objects.get(username=username)
	return user.groups.filter(name='Muted').exists()
