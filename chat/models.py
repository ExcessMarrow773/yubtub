from django.db import models
from yubtub import settings

# Create your models here.

User = settings.AUTH_USER_MODEL


class Message(models.Model):
	from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE)
	to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE)
	body = models.TextField()
	sent_on = models.DateTimeField(auto_now_add=True)


	class Meta:
		verbose_name = "Message"
		verbose_name_plural = "Messages"
		ordering = ('sent_on',)

	def __str__(self):
		return f"Message {self.id} in chat {self.chat.id}"
