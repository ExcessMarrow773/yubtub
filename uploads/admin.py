from django.contrib import admin

from .models import Upload

# Register your models here.

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
	list_display = ('name', 'downloads', 'file_name', 'uploaded_on')
	list_filter = ('name', 'downloads', 'uploaded_on')
	readonly_fields = ('downloads',)

	date_hierarchy = 'uploaded_on'
	search_fields = ('body', 'file_name')