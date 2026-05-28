from django.contrib import admin
from bugs.models import BugReport

# Register your models here.
@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'type', 'has_github_issue', 'resolved', 'created_on')
    list_filter = ('has_github_issue', 'created_on', 'resolved', 'type')
    date_hierarchy = 'created_on'
    search_fields = ('title', 'author', 'body')