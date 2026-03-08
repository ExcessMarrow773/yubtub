from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from itertools import chain
from operator import attrgetter

from uploads.forms import UploadFileForm
from uploads.models import Upload

from app.views import getUserFromID
from app import mail

import json

User = get_user_model()
# Create your views here.

def index(request):
	context = {

	}
	return render(request, "uploads/index.html", context)

@login_required()
def createUpload(request):
	user = getUserFromID(request.user.id)

	if request.method == "POST":
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			upload = Upload(
				author=user.pk,
				name=form.cleaned_data["name"],
				file=request.FILES["file"],
				file_name=request.FILES["file"].name
			)
			upload.save()
			return redirect('uploads:view', upload.pk)
	else:
		form = UploadFileForm()

	context = {
		'form': form
	}
	return render(request, "uploads/create.html", context)

def viewUpload(request, pk):
	user = getUserFromID(request.user.id)
	upload = get_object_or_404(Upload, pk=pk)
	print(upload.file_name)
	context = {
		'upload': upload
	}
	return render(request, "uploads/view.html", context)