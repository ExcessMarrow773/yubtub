from django.contrib import admin
from app.models import Video, VideoComment, Post, PostComment, BugReport
# Register your models here.

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass

@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    pass

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    pass

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    pass