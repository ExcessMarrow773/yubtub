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
        Group messages by conversation (A ↔ B, not just A → B)
        and pass them to the template.
        """
        qs = self.get_queryset(request).order_by('-sent_on')

        conversations = {}
        for message in qs:
            # Create a direction-independent key for the pair of users
            user_pair = tuple(sorted([message.from_user, message.to_user], key=lambda u: u.id))
            conversations.setdefault(user_pair, []).append(message)

        extra_context = extra_context or {}
        extra_context['conversations'] = conversations.items()
        return super().changelist_view(request, extra_context=extra_context)
