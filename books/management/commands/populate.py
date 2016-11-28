from django.core.management import call_command
from django.core.management.base import BaseCommand


from faker import Factory as FakerFactory

from books.models import add_book_copy, Customer

# Set up faker object
faker = FakerFactory.create('en_GB')


books = (
    # No Starch Press
    '9781593272074', '9781593271749', '9781593273842', '9781593275990',
    '9781593272067', '9781593271473', '9781593276515', '9781593272944',
    '9781593275754', '9781593277499', '9781593276492', '9781593274085',
    '9781593273897', '9781593274870', '9781593270773', '9781593275204',
    '9781593275402', '9781593276034', '9781593274078', '9781593276041',
    '9781593275723', '9781593274917', '9781593271480', '9781593275273',
    '9781593275662', '9781593277628', '9781593276126', '9781593270476',
    '9781593274245', '9781593273972', '9781593270612', '9781593270629',
    '9781593271732', '9781593271824', '9781593270124', '9781593270032',
    '9781593270568', '9781593272814', '9781593275914', '9781593274351',
    '9781593272838',
)


class Command(BaseCommand):
    """
    Populates the imageboard with fake test data
    """
    help = 'Populates the database with mock data'

    def handle(self, *args, **options):
        self.stdout.write('Populating Database...')

        # Flush the Database of old data, suppress prompt
        call_command('flush', '--noinput')

        for i in range(10):
            Customer.objects.create_user(
                first_name=faker.first_name(), last_name=faker.last_name(),
                email=faker.email(), password='test', username=faker.name()
            )

        for isbn in books:
            add_book_copy(isbn)

        self.stdout.write(self.style.SUCCESS('Done'))
