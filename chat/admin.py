from django.contrib import admin
from chat.models import Message
# Register your models here.

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'sent_on')
    list_filter = ('sent_on',)
    date_hierarchy = 'sent_on'
    search_fields = ('from_user', 'to_user', 'body')