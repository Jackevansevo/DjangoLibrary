from django.contrib import admin

from .models import Author, Book, BookCopy, Customer, Genre, Loan


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'subtitle')
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        # If the object is new create an inital copy
        if not change:
            BookCopy.objects.get_or_create(book=obj)
        obj.save()


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'join_date', 'book_allowance')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'returned')
