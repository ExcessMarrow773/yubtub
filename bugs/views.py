from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from bugs.forms import BugReportForm
from bugs.models import BugReport

from itertools import chain
from operator import attrgetter

from app import mail

import json

User = get_user_model()
# Create your views here.

def bug_report(request):
    if request.method == "POST":
        form = BugReportForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                username='AnonymousUser'
            else:
                username=request.user.username
            bug = BugReport(
                author=username,
                title=form.cleaned_data["title"],
                body=form.cleaned_data["body"],
                type=form.cleaned_data["type"],
                github_issue=form.cleaned_data["github_issue"]
            )
            if bug.github_issue != None:
                bug.has_github_issue = True
            bug.save()
            return redirect('app:index')
    else:
        form = BugReportForm()
    context = {
        'form': form
    }
    return render(request, "bugs/bugReport.html", context)

def bug_reportIndex(request):
    bugs = BugReport.objects.order_by('created_on').order_by('-created_on').filter(resolved=False)
    resolvedBugs = BugReport.objects.order_by('created_on').filter(resolved=True)
    
    combined = bugs | resolvedBugs

    authors = {}
    for i in combined:
          user = User.objects.get(id=i.author).username
          authors[i.author] = user

    context = {
         'resolvedBugs': resolvedBugs,
         'bugs': bugs,
         'authors': authors
    }
    return render(request, 'bugs/bugReportIndex.html', context)

def bugView(request, pk):
    bug = get_object_or_404(BugReport, pk=pk)
    username = User.objects.get(id=bug.author).username

    context = {
        'bug': bug,
        'username': username
    }

    return render(request, 'bugs/bugView.html', context)

@require_POST
def resolveBug(request):
	if not request.user.is_authenticated:
		return JsonResponse({'message': 'Login required'}, status=403)

	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'message': 'Invalid JSON'}, status=400)


	bug=data.get('bug')

	try:
		bug = BugReport.objects.get(pk=bug)
	except User.DoesNotExist:
		return JsonResponse({'message': 'User not found.'}, status=404)

	if bug.resolved:
		bug.resolved = False
		return JsonResponse({'message': 'Opened bug'})
	else:
		bug.resolved = True
		return JsonResponse({'message': 'Bug Resolved'})