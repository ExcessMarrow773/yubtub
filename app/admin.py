from django.contrib import admin
from app.models import Video, VideoComment, Post, PostComment, Banner
# Register your models here.

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_on', 'views', 'likes')
    list_filter = ('created_on',)
    date_hierarchy = 'created_on'
    search_fields = ('title', 'author')

@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'video', 'created_on')
    list_filter = ('created_on',)
    date_hierarchy = 'created_on'
    search_fields = ('author', 'body')

@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_on')
    list_filter = ('created_on',)
    date_hierarchy = 'created_on'
    search_fields = ('title', 'author')

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_on')
    list_filter = ('created_on',)
    date_hierarchy = 'created_on'
    search_fields = ('author', 'body')

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('message','active', 'created_on')
    list_filter = ('created_on',)
    date_hierarchy = 'created_on'