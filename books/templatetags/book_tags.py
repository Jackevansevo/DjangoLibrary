from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter(name="getReviewStars")
def getReviewStars(value):
    star = "<i class='fa gold fa-star' aria-hidden='true'></i>"
    return mark_safe(star*(int(round(value))))
