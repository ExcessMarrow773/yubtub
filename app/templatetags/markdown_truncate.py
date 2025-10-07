from django import template
from django.utils.html import strip_tags
import markdown

register = template.Library()

@register.filter
def markdown_truncate(value, length):
    """
    Render Markdown and truncate the resulting text to the specified length.
    markdown.markdown(value, extensions=['fenced_code'])
    """
    rendered = markdown.markdown(value, extensions=['fenced_code'])  # Render Markdown
    plain_text = strip_tags(rendered)  # Remove HTML tags
    return rendered[:length] + ("..." if len(plain_text) > length else "")