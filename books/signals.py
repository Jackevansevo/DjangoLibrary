from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Book


@receiver(post_save, sender=Book)
def my_handler(sender, **kwargs):
    print(sender)
