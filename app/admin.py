from django.contrib import admin
from app.models import Video, VideoComment, Post, PostComment
# Register your models here.

class VideoAdmin(admin.ModelAdmin):
    pass

class VideoCommentAdmin(admin.ModelAdmin):
    pass

class PostsAdmin(admin.ModelAdmin):
    pass

class PostCommentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Video, VideoAdmin)
admin.site.register(VideoComment, VideoCommentAdmin)
admin.site.register(Post, PostsAdmin)
admin.site.register(PostComment, PostCommentAdmin)