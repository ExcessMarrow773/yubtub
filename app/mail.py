from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.templatetags.static import static
from django.utils.safestring import mark_safe

import threading
import markdown

User = get_user_model()

def email_deamon(email):
	print("Sending email in Deamon")
	email.send()

def mention_email(user, message, type, url="https://atticusfw.dev"):
	context = {
		"message": message,
		"url": url
	}
	html_content = render_to_string('mail/mention.html')
	rendered_template = Template(html_content).render(Context(context))
	
	html = markdown.markdown(
		rendered_template,
		extensions=['fenced_code', 'attr_list', 'nl2br']
	)
	markdown_html_content = mark_safe(html)
	user = [*user]
	users = []
	for i in user:
		users.append(get_object_or_404(User, username=i).email)
	print(users)

	types = {
		'message': 'message',
		'desc': 'description',
		'post': 'post'
	}

	email = EmailMessage(
		f"You have been mentioned in Yubtub {types[str(type)]} {url}",
		markdown_html_content,
		"YubTub Server Email <spector.studio.games@gmail.com",
		bcc=users
	)

	email.content_subtype = "html"

	# email.send()
	x = threading.Thread(target=email_deamon, args=(email,), daemon=False)
	x.start()

