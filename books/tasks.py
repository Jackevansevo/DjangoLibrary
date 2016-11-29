from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.schedules import crontab
from celery.decorators import periodic_task


from django.core.mail import send_mail, send_mass_mail
from django.utils.timezone import now
from django.conf import settings
from .models import Customer


def send_async_email(subject, message, recipients):
    send_mail(
        subject,
        message,
        settings.EMAIL,
        recipients,
    )


@shared_task
def send_async_email_batch(subject, message, recipients):
    send_mass_mail(
        subject,
        message,
        recipients,
    )


# hour=7, minute=30
@shared_task
@periodic_task(run_every=(crontab()), name="daily_send_reminder_emails")
def daily_send_reminder_emails():
    customers = Customer.objects.filter(
        loans__returned=False, loans__end_date__lte=now()
    )
    for customer in customers:
        book_titles = "\n".join(customer.unreturned_loans.values_list(
            'book_copy__book__title', flat=True))
        send_async_email(
            'DjangoLibrary book return request',
            'Please return the following books: \n' + book_titles,
            [customer.email]
        )
