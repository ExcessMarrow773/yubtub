from django.contrib import admin
from app.models import Video, Comment
# Register your models here.

class VideoAdmin(admin.ModelAdmin):
    pass

class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)