from django.contrib import admin
from chat.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'sent_on')
    list_filter = ('sent_on',)
    date_hierarchy = 'sent_on'
    search_fields = ('from_user__username', 'to_user__username', 'body')
    ordering = ('from_user', 'to_user', '-sent_on')

    def changelist_view(self, request, extra_context=None):
        """
        Override the change list view to group messages by conversation (from_user → to_user)
        and pass it to the template.
        """
        qs = self.get_queryset(request).order_by('from_user', 'to_user', '-sent_on')

        # Group into dict: {(from_user, to_user): [messages]}
        conversations = {}
        for message in qs:
            key = (message.from_user, message.to_user)
            conversations.setdefault(key, []).append(message)

        extra_context = extra_context or {}
        extra_context['conversations'] = conversations.items()
        return super().changelist_view(request, extra_context=extra_context)
