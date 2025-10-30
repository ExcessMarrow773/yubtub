from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def follow_system_account(sender, instance, created, **kwargs):
    try:
        system_account = User.objects.get(username='system')  # Replace 'system' with the actual username of the system account
        instance.following.add(system_account)  # Assuming a ManyToMany field named 'following'\
        system_account.following.add(instance)  # Make the relationship mutual
        system_account.unfollow(system_account)
    except User.DoesNotExist:
        pass
