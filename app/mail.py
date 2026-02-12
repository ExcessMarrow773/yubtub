from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import threading

User = get_user_model()

def email_deamon(email):
	print("Sending email in Deamon")
	email.send()

def mention_email(user, message):
	context = {
		"message": message
	}
	html_content = render_to_string('mail/mention.html', context)
	user = [*user]
	users = []
	for i in user:
		users.append(get_object_or_404(User, username=i).email)
	print(users)
	email = EmailMessage(
		"You have been mentioned in a Yubtub message",
		html_content,
		"YubTub",
		users
	)

	email.content_subtype = "html"

	# email.send()
	x = threading.Thread(target=email_deamon, args=(email,), daemon=True)
	x.start()