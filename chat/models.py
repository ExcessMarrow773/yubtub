from django.db import models
from yubtub import settings

# Create your models here.

User = settings.AUTH_USER_MODEL

class Chat(models.Model):
	to_user = models.CharField(max_length=150)
	by_user = models.CharField(max_length=150)

	class Meta:
		verbose_name = "chat"
		verbose_name_plural = "chats"

	def __str__(self):
		return self.name

class Message(models.Model):
	chat = models.ForeignKey("chat.Chat", related_name='messages', on_delete=models.CASCADE)
	sender = models.CharField(max_length=150)
	body = models.TextField()
	sent_on = models.DateTimeField(auto_now_add=True)


	class Meta:
		verbose_name = "Message"
		verbose_name_plural = "Messages"
		ordering = ('sent_on',)

	def __str__(self):
		return f"Message {self.id} in chat {self.chat.id}"
