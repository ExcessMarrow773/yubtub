from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from itertools import chain
from operator import attrgetter

from app import mail

import json

User = get_user_model()
# Create your views here.

def index(request):
	context = {

	}
	return render(request, "uploads/index.html", context)