from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter(name="getReviewStars")
def getReviewStars(value):
    string = ""
    for i in range(int(round(value))):
        string += "<i class='fa gold fa-star' aria-hidden='true'></i>"
    return mark_safe(string)
