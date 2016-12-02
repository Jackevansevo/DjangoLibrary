from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView

from .forms import BookCreateForm, BookReviewForm
from .models import Author, Book, Customer, Genre, Loan, add_book_copy
from .tasks import send_reminder_emails


def index(request):
    overdue_loans = Loan.overdue.select_related('customer')
    latest_books = Book.objects.all()[:5]
    context = {'overdue_loans': overdue_loans, 'latest_books': latest_books}
    return render(request, 'books/index.html', context)


def book_list(request):
    if request.method == 'POST':
        if request.POST.get('query'):
            return redirect('books:book-search', request.POST['query'])
    book_list = Book.objects.prefetch_related(
        'authors',
        Prefetch('copies__loans', queryset=Loan.objects.filter(returned=False))
    )
    paginator = Paginator(book_list, 40)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        books = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        books = paginator.page(paginator.num_pages)
    return render(request, 'books/book_list.html', {'books': books})


def book_search(request, query):
    books = Book.objects.prefetch_related('authors')\
        .filter(title__search=query)
    return render(request, 'books/book_list.html', {'books': books})


@login_required
def book_create(request):
    """Simple view to add a book"""
    form = BookCreateForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            book = add_book_copy(form.cleaned_data['isbn'])
            return redirect('books:book-detail', slug=book.slug)
    else:
        form = BookCreateForm()
    context = {'form': form}
    return render(request, 'books/book_create.html', context)


def book_detail(request, slug):
    book = get_object_or_404(
        Book.objects.prefetch_related('reviews'), slug=slug)
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            form.instance.book = book
            form.instance.customer = request.user
            form.instance.save()
            return redirect(book)
    else:
        form = BookReviewForm()
    has_loaned, has_book, has_reviewed = False, False, False
    if request.user.is_authenticated:
        has_book = request.user.has_book(book.isbn)
        has_loaned = request.user.has_loaned(book.isbn)
        has_reviewed = request.user.has_reviewed(book.isbn)
    context = {
        'book': book, 'user_has_book': has_book, 'form': form,
        'user_has_loaned': has_loaned, 'has_reviewed': has_reviewed
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
        if request.POST.get('query'):
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
def send_overdue_reminder_emails(self):
    """End point trigger to manually send off overdue loan reminder emails """
    send_reminder_emails.apply()
    return redirect('books:index')


@login_required
def book_checkout(request, slug):
    book = get_object_or_404(Book, slug=slug)
    customer = request.user
    if customer.can_loan:
        if book.is_available:
            book_copy = book.get_available_copy()
            Loan.objects.create(customer=customer, book_copy=book_copy)
        else:
            messages.error(request, 'Book Unavailable')
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
    return redirect(book)


@login_required
@require_http_methods(['POST'])
def bulk_return(request, pk):
    """Returns all outstanding book loans for a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    for loan in customer.unreturned_loans:
        loan.returned = True
        loan.save(update_fields=['returned'])
    return redirect(customer)
