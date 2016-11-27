from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Author, Book, Genre, Loan, add_book_copy
from .forms import BookCreateForm


def index(request):
    return render(request, 'books/index.html')


def book_list(request):
    if request.method == 'POST':
        query = request.POST['query']
        return redirect('books:book-search', query=query)
    books = Book.objects.all()
    context = {'book_list': books}
    return render(request, 'books/book_list.html', context=context)


def book_search(request, query):
    books = Book.objects.filter(title__search=query)
    return render(request, 'books/book_list.html', {'book_list': books})


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
    book = get_object_or_404(Book, slug=slug)
    context = {'book': book, 'user_has_book': request.user.has_book(book.isbn)}
    return render(request, 'books/book_detail.html', context)


def author_detail(request, slug):
    author = get_object_or_404(
        Author.objects.prefetch_related('books'), slug=slug)
    context = {'author': author}
    return render(request, 'books/author_detail.html', context=context)


def customer_detail(request):
    return render(request, 'books/customer_detail.html')


class GenreList(ListView):
    model = Genre


def genre_list(request):
    if request.method == 'POST':
        query = request.POST['query']
        return redirect('books:genre-search', query=query)
    genres = Genre.objects.all()
    context = {'genre_list': genres}
    return render(request, 'books/genre_list.html', context=context)


def genre_search(request, query):
    genres = Genre.objects.filter(name__search=query)
    return render(request, 'books/genre_list.html', {'genre_list': genres})


class GenreDetail(DetailView):
    model = Genre


@require_http_methods(['POST'])
def book_checkout(request, slug):
    book = get_object_or_404(Book, slug=slug)
    customer = request.user
    if customer.can_loan:
        if book.is_available:
            book_copy = book.get_available_copy()
            Loan.objects.create(customer=customer, book_copy=book_copy)
        else:
            messages.error(request, 'Book Unavailable')
    return redirect(book)


@require_http_methods(['POST'])
def book_return(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if request.user.has_book(book.isbn):
        loan = request.user.get_unreturned_book_loan(book.isbn)
        loan.returned = True
        loan.save(update_fields=["returned"])
    return redirect(book)
