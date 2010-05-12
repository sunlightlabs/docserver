from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def generic_paginator(page_obj, paginator):
    return render_to_string("public_site/generic_paginator.html", {'page_obj':page_obj, 'paginator':paginator})
