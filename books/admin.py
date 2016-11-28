from django.contrib import admin

from .models import Author, Book, Customer, Genre, Loan


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle')
    prepopulated_fields = {'slug': ('title',)}


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'join_date', 'book_allowance')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class LoanAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'returned')


admin.site.register(Book, BookAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Loan, LoanAdmin)
