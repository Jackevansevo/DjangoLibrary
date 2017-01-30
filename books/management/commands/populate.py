from django.core.management import call_command
from django.core.management.base import BaseCommand


from faker import Factory as FakerFactory

from books.models import Book, BookCopy, Customer

# Set up faker object
faker = FakerFactory.create('en_GB')


# Random assortment of books
books = [
    '9780062005854', '9781904915010', '9780553347593', '9780374530419',
    '9780596520120', '9780465067107', '9780307887894', '9780571303663',
    '9781620402771', '9780887309373', '9780804139298', '9780544272996',
    '9780141047973', '9781119942535', '9780596001087', '9780387948607',
    '9780670879830', '9780596516499', '9780066620992', '9780062276698',
    '9780691168319', '9781491950357',  '9781780324500', '9781593272821',
    '9780804139021', '9780345341846', '9780060929879', '9780761169086',
    '9780749475093', '9781594205552', '9780743217347', '9781476753652',
    '9781592406593', '9781455586691', '9781617230172', '9780691149134',
    '9780670069972', '9781781688458', '9781846147388', '9780062407801',
    '9780241258156', '9781408706763', '9780312535742', '9781884829987',
    '9780385689229', '9781591844686', '9780393254594', '9781593272814',
    '9781593272838', '9781593274351', '9781593275914', '9781593270568',
    '9781593270032', '9781593270124', '9781593271824', '9781593271732',
    '9781593270629', '9781593270612', '9781593273972', '9781593274245',
    '9781593270476', '9781593276126', '9781593275662', '9781593275273',
    '9781593271480', '9781593274917', '9781593275723', '9781593276041',
    '9781593274078', '9781593276034', '9781593275204', '9781593270773',
    '9781593274870', '9781593273897', '9781593274085', '9781593276492',
    '9781593275754', '9781593272944', '9781593276515', '9781593271473',
    '9781593272067', '9781593275990', '9781593273842', '9781593271749',
    '9781593272074'
]


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
            print(isbn)
            BookCopy.objects.create(
                book=Book.objects.create_book_from_metadata(isbn))

        self.stdout.write(self.style.SUCCESS('Done'))
