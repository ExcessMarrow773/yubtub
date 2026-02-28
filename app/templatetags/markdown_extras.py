from django import template
from django.template import Template, Context
from django.templatetags.static import static
from django.utils.safestring import mark_safe

import markdown

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(value):
    markdown_with_load = "{% load static %}\n" + value
    rendered_template = Template(markdown_with_load).render(Context({}))
    html = markdown.markdown(
        rendered_template,
        extensions=['fenced_code', 'attr_list', 'nl2br']
    )
    return mark_safe(html)