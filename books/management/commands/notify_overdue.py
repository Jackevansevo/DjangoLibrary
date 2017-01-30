from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template import Context
from django.template.loader import get_template
from django.utils.timezone import now

from books.models import Customer


class Command(BaseCommand):

    help = "Sends overdue loan reminder emails to customers"

    def handle(self, *args, **options):
        customers = Customer.objects.filter(loans__returned=False,
                                            loans__end_date__lte=now())
        for customer in customers:
            self.stdout.write(self.style.SUCCESS(
                'Sending reminder to {}'.format(customer)))
            context = {'customer': customer}
            html = get_template('books/email.html').render(Context(context))
            message = "Return books reminder"
            send_mail('DjangoLibrary book return request', message,
                      settings.EMAIL_SENDER, [customer.email], html)
