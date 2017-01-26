from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "books"
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^books/$', views.book_list, name='book-list'),

    url(r'^books/create/$', views.book_create, name='book-create'),

    url(r'^books/bulk-return/$', views.bulk_return, name='bulk-return'),

    url(r'^books/(?P<slug>[\w-]+)/$', views.book_detail,
        name='book-detail'),

    url(r'^books/(?P<slug>[\w-]+)/update/$', views.BookUpdateView.as_view(),
        name='book-update'),

    url(r'^books/(?P<slug>[\w-]+)/delete/$', views.BookDeleteView.as_view(),
        name='book-delete'),

    url(r'^books/(?P<slug>[\w-]+)/checkout/$', views.book_checkout,
        name='book-checkout'),

    url(r'^books/(?P<slug>[\w-]+)/return/$', views.book_return,
        name='book-return'),

    url(r'^books/(?P<slug>[\w-]+)/renew/$', views.book_renew_loan,
        name='book-loan-renew'),

    url(r'^send-overdue-reminders/$', views.send_overdue_reminder_emails,
        name='send-overdue-reminders'),

    url(r'^authors/(?P<slug>[\w-]+)$', views.author_detail,
        name='author-detail'),

    url(r'^genres/$', views.genre_list, name='genre-list'),

    url(r'^genres/search/(?P<query>[\w-]+)$', views.genre_search,
        name='genre-search'),

    url(r'^genres/(?P<slug>[\w-]+)$', views.GenreDetail.as_view(),
        name='genre-detail'),

    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^accounts/profile/$', views.customer_detail, name='customer-detail'),
]
