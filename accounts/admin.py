from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
	readonly_fields = ('followers_display', 'follower_count')
	
	fieldsets = (
		(None, {
			'fields': ('username', 'password')
		}),
		('Personal info', {
			'fields': ('first_name', 'last_name', 'email')
		}),
		('Permissions', {
			'fields': (
				'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
			)
		}),
		('Important dates', {
			'fields': ('last_login', 'date_joined')
		}),
		('Community info', {
			'fields': ('following', 'follower_count', 'followers_display')
		})
	)
	def followers_display(self, obj):
	        return ", ".join([user.username for user in obj.followers.all()])
	followers_display.short_description = 'Followers'

	def follower_count(self, obj):
		return obj.followers.count()
	follower_count.short_description = 'Follower Count'

admin.site.register(CustomUser, CustomUserAdmin)