from django import template
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()


@register.filter
def get_user_username(id, requestUser):
    user = User.objects.get(id=id)
    username = user.username
    if requestUser.is_superuser:
        output = f"{username} ({user.first_name} {user.last_name})"
    else:
        output = username
    return output
