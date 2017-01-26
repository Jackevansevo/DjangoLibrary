from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def on_logged_in(sender, user, request, **kwargs):
    login_message = "Logged in as: {}!".format(user.username)
    messages.success(request, login_message, fail_silently=True)


@receiver(user_logged_out)
def on_logged_out(sender, user, request, **kwargs):
    logout_message = "Logged out from: {}!".format(user.username)
    messages.success(request, logout_message, fail_silently=True)
