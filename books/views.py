from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from .forms import BookQuickCreateForm, BookReviewForm, BookForm
from .models import Author, Book, BookCopy, CustomerBook, Genre, Loan, Review
from .tasks import send_reminder_emails


def index(request):
    overdue_loans = Loan.overdue.select_related('customer')
    latest_books = Book.objects.all()[:5]
    context = {'overdue_loans': overdue_loans, 'latest_books': latest_books}
    return render(request, 'books/index.html', context)


def paginate(request, objects, page_count=100):
    paginator = Paginator(objects, page_count)
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)
    return objects


def book_list(request):
    books = Book.available.prefetch_related('authors')
    if request.GET.get('q'):
        books = books\
            .annotate(search=SearchVector('title', 'subtitle'))\
            .filter(search=request.GET['q'])
    return render(request, 'books/book_list.html', {
        'books': paginate(request, books)
    })


class BookCreate(CreateView):
    form = BookForm
    model = Book


@login_required
def book_create(request):
    """Simple view to add a book"""
    isbn_form = BookQuickCreateForm(request.POST)
    book_form = BookForm(request.POST)

    # [TODO] Fix this broken shit

    if request.method == 'POST':

        if 'isbn_form' in request.POST and isbn_form.is_valid():
            isbn = isbn_form.cleaned_data['isbn']
            book = Book.objects.create_book_from_metadata(isbn)
            BookCopy.objects.create(book=book)
            return redirect('books:book-detail', slug=book.slug)

        elif 'book_form' in request.POST and book_form.is_valid():
            book = book_form.save()
            return redirect('books:book-detail', slug=book.slug)

    else:
        isbn_form = BookQuickCreateForm()
        book_form = BookForm()

    context = {'isbn_form': isbn_form, 'book_form': book_form}
    return render(request, 'books/book_create.html', context)


def book_detail(request, slug):
    book = get_object_or_404(
        Book.objects.prefetch_related(
            Prefetch(
                'copies',
                queryset=BookCopy.objects.prefetch_related(
                    Prefetch(
                        'loans',
                        queryset=Loan.objects.select_related('customer')
                    )
                )
            ),
            Prefetch(
                'reviews',
                queryset=Review.objects.select_related('customer')
            ),
            'authors',
        ),
        slug=slug)

    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            form.instance.book = book
            form.instance.customer = request.user
            form.instance.save()
            return redirect(book)
    else:
        review_form = BookReviewForm()

    has_reviewed, has_loaned, unreturned_loan = False, False, None
    has_read, wants_book = False, False

    # Collect some necessary page data
    if request.user.is_authenticated:
        has_reviewed = request.user.has_reviewed(book.isbn)
        has_loaned = request.user.has_loaned(book.isbn)
        unreturned_loan = request.user.get_unreturned_book_loan(book.isbn)
        has_read = request.user.books.filter(
            book=book, category='R').exists()
        wants_book = request.user.books.filter(
            book=book, category='W').exists()

    context = {
        'book': book,
        'user_wants_book': wants_book,
        'user_has_read': has_read,
        'review_form': review_form,
        'user_has_loaned': has_loaned,
        'user_has_reviewed': has_reviewed,
        'unreturned_loan': unreturned_loan
    }
    return render(request, 'books/book_detail.html', context)


@method_decorator(login_required, name='dispatch')
class BookUpdateView(UpdateView):
    model = Book
    fields = ('title', 'subtitle', 'img', 'authors', 'genres')
    template_name_suffix = '_update_form'


@method_decorator(login_required, name='dispatch')
class BookDeleteView(DeleteView):
    model = Book
    success_url = reverse_lazy('books:book-list')


def author_detail(request, slug):
    author = get_object_or_404(
        Author.objects.prefetch_related('books'), slug=slug)
    context = {'author': author}
    return render(request, 'books/author_detail.html', context=context)


@login_required
def customer_detail(request):
    return render(request, 'books/customer_detail.html')


def genre_list(request):
    if request.method == 'POST':
        if request.POST.get('query'):  # Ignore empty search queries
            return redirect('books:genre-search', query=request.POST['query'])
    genres = Genre.objects.all()
    context = {'genre_list': genres}
    return render(request, 'books/genre_list.html', context=context)


def genre_search(request, query):
    genres = Genre.objects.filter(name__search=query)
    return render(request, 'books/genre_list.html', {'genre_list': genres})


class GenreDetail(DetailView):
    model = Genre


@login_required
@require_http_methods(['POST'])
def book_renew_loan(request, slug):
    """End point to renew logged in users' loan for a given book"""
    book = get_object_or_404(Book, slug=slug)
    # Check that the user currently has the book
    if request.user.has_book(book):
        loan = request.user.get_unreturned_book_loan(book)
        try:
            loan.renew()
        except ValidationError:
            messages.error(request, 'Loan not renewable')
        finally:
            messages.success(request, 'Loan renewed')
    # Redirect to the next page, or book's page as fallback
    return redirect(request.POST.get('next', book))


@login_required
@require_http_methods(['POST'])
def send_overdue_reminder_emails(self):
    """End point trigger to manually send off overdue loan reminder emails """
    send_reminder_emails.apply()
    return redirect('books:index')


@login_required
def book_checkout(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.user.can_loan:
        if request.user.can_loan_book(book):
            if book.is_available:
                book_copy = book.get_available_copy()
                Loan.objects.create(customer=request.user, book_copy=book_copy)
            else:
                messages.error(request, 'Book Unavailable')
        else:
            messages.error(request, 'Cant check out duplicate book copies')
    else:
        messages.error(request, 'Reached loan limit')
    return redirect(book)


@login_required
@require_http_methods(['POST'])
def book_return(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.user.has_book(book.isbn):
        loan = request.user.get_unreturned_book_loan(book.isbn)
        loan.returned = True
        loan.save(update_fields=['returned'])
        messages.success(request, 'Returned Book: {}'.format(book.title))
    return redirect(book)


@login_required
def add_book_to_want_list(request, slug):
    book = get_object_or_404(Book, slug=slug)
    CustomerBook.objects.create(book=book, customer=request.user, category='W')
    messages.success(request, 'Added Book: {} to list'.format(book.title))
    return redirect(book)


@login_required
@require_http_methods(['POST'])
def bulk_return(request):
    """Returns all outstanding book loans for a customer"""
    for loan in request.user.unreturned_loans:
        loan.returned = True
        loan.save(update_fields=['returned'])
        messages.success(request, 'All outstanding loans returned')
    return redirect(request.user)
