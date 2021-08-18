from django.template import Library
from Bookshop.settings import MEDIA_URL
register = Library()

@register.simple_tag
def media_url():
    return MEDIA_URL