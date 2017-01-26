from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter(name="prettystars")
def review_stars(value):
    star = "<i class='fa fa-star text-warning' aria-hidden='true'></i>"
    return mark_safe(star*(int(round(value))))
