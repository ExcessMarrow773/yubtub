from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import ProfileDetailsChange, ProfilePasswordChange, ProfileUsernameChange


from itertools import chain
from operator import attrgetter
import os
import json

User = get_user_model()

# Create your views here.


@login_required(login_url='/login/')
def settings(request):
	print(request.POST)
	userModel = get_object_or_404(User, username=request.user.username)

	if request.method == "POST":
		if 'changeUsername/' in request.path:
			form = ProfileUsernameChange(request.POST, instance=userModel)
		elif 'changePassword/' in request.path:
			form = ProfilePasswordChange(user=request.user, data=request.POST)
		else:
			form = ProfileDetailsChange(request.POST, request.FILES, instance=userModel)
		if form.is_valid():
			form.save()
			return redirect('accounts:settings')
	else:
		if 'changeUsername/' in request.path:
			form = ProfileUsernameChange(instance=userModel)
		elif 'changePassword/' in request.path:
			form = ProfilePasswordChange(user=request.user)
		else:
			form = ProfileDetailsChange(instance=userModel)

	context = {'form': form, 'mymodel_instance': userModel}

	return render(request, 'accounts/settings.html', context)