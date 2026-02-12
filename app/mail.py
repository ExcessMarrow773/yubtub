from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

User = get_user_model()
def mention_email(user, message):
	context = {
		"message": message
	}
	html_content = render_to_string('mail/mention.html', context)
	print(*user)
	email = EmailMessage(
		"You have been mentioned in a Yubtub message",
		html_content,
		"spector.studio.games@gmail.com",
		['atticus.falkner.walton@gmail.com']
	)

	email.content_subtype = "html"

	email.send()