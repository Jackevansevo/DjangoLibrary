from django.contrib.auth.models import AbstractUser
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone

from titlecase import titlecase

from .isbn import meta


class TimeStampedModel(models.Model):
    """Adds created_on, and modified_on Fields to all subclasses"""
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(AbstractUser):
    join_date = models.DateTimeField(auto_now_add=True)
    book_allowance = models.IntegerField(default=3)

    def has_book(self, isbn):
        """Returns True if a customer currently has a book"""
        return self.unreturned_loans.filter(
            book_copy__book__isbn=isbn).exists()

    def has_loaned(self, isbn):
        """Returns True if a user has previously loaned a book"""
        return self.loans.filter(book_copy__book_isbn=isbn).exists()

    def get_unreturned_book_loan(self, isbn):
        return self.unreturned_loans.filter(book_copy__book=isbn).first()

    @property
    def can_loan(self):
        """Returns True if customer is allowed to currently loan books"""
        return self.unreturned_loans.count() < self.book_allowance

    @property
    def unreturned_loans(self):
        """Returns Queryset containing a customer unreturned loans"""
        return self.loans.filter(returned=False)

    @property
    def read_list(self):
        """Returns set of all books a customer has previously loaned"""
        return Book.objects.filter(copies__loans__customer=self).distinct()

    def __str__(self):
        return self.username


class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Author, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:author-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Genre, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:genre-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Book(TimeStampedModel):
    isbn = models.CharField(max_length=13, primary_key=True)
    title = models.CharField(max_length=200, db_index=True, unique=True)
    subtitle = models.CharField(max_length=200)
    img = models.URLField()
    slug = models.SlugField()

    authors = models.ManyToManyField('Author', related_name='books')
    genres = models.ManyToManyField('Genre', related_name='books')

    @property
    def author_names(self):
        return ", ".join(author.name for author in self.authors.all)

    @property
    def is_available(self):
        """Returns True if any copies aren't currently on loan"""
        return not self.copies.filter(loans__returned=False).exists()

    @property
    def num_available_copies(self):
        return len([c for c in self.copies.all() if not c.on_loan])

    @property
    def num_copies(self):
        return self.copies.count()

    def get_available_copy(self):
        return self.get_available_copies()[0]

    def get_available_copies(self):
        return [c for c in self.copies.all() if not c.on_loan]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:book-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class BookCopy(models.Model):
    book = models.ForeignKey('Book', related_name='copies')

    @property
    def on_loan(self):
        """Returns True if a book copy has any outstanding loans"""
        return self.loans.filter(returned=False).exists()


class Loan(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    returned = models.BooleanField(default=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                 null=True, related_name='loans')
    book_copy = models.ForeignKey(
        'BookCopy', on_delete=models.CASCADE, related_name='loans')

    def save(self, *args, **kwargs):
        self.start_date = timezone.now()
        self.end_date = self.start_date + timezone.timedelta(days=7)
        super(Loan, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.start_date)


def create_book(isbn):
    book, created = Book.objects.get_or_create(isbn=isbn)
    if created:
        # If the book is new, populate it's fields
        meta_info = meta(isbn)
        book.title = titlecase(meta_info.get('title', ''))
        book.subtitle = titlecase(meta_info.get('subtitle', ''))
        book.img = meta_info.get('img')
        # Save the Book
        book.save()

        # Add the ManyToMany related authors
        for name in meta_info.get('authors', []):
            name = titlecase(name)
            author, created = Author.objects.get_or_create(name=name)
            book.authors.add(author)

        for name in meta_info.get('categories', []):
            name = titlecase(name)
            genre, created = Genre.objects.get_or_create(name=name)
            book.genres.add(genre)
    return book


def add_book_copy(isbn):
    book = create_book(isbn)
    BookCopy.objects.create(book=book)
    return book
