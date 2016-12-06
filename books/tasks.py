from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.schedules import crontab
from celery.decorators import periodic_task

from django.template import Context
from django.template.loader import get_template
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

from .models import Customer


@shared_task
def send_async_email(subject, message, from_email, recipient_list, html):
    send_mail(subject, message, from_email, recipient_list, html_message=html)


@periodic_task(run_every=(crontab()), name="daily_send_reminder_emails")
def send_reminder_emails():
    customers = Customer.objects.filter(loans__returned=False,
                                        loans__end_date__lte=now())
    for customer in customers:
        context = {'customer': customer}
        html = get_template('books/email.html').render(Context(context))
        message = "Return books reminder"
        send_async_email('DjangoLibrary book return request', message,
                         settings.EMAIL_SENDER, [customer.email], html)
