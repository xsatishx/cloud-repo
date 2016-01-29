from django import template
from tukey.content.models import Page

register = template.Library()

@register.inclusion_tag('nav.html')
def show_nav(curr_page):
    nav_pages = Page.objects.filter(nav_order__gte='0').order_by('nav_order')
    return {'nav_pages' : nav_pages, 'curr_page' : curr_page}

