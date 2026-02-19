from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from bugs.forms import BugReportForm
from bugs.models import BugReport


from app import mail

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

    context = {
         'resolvedBugs': resolvedBugs,
         'bugs': bugs
    }
    return render(request, 'bugs/bugReportIndex.html', context)

def bugView(request, pk):
    bug = get_object_or_404(BugReport, pk=pk)

    context = {
        'bug': bug
    }

    return render(request, 'bugs/bugView.html', context)