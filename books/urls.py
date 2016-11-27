from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "books"
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^books/$', views.book_list, name='book-list'),

    url(r'^books/search/(?P<query>[\w-]+)$', views.book_search,
        name='book-search'),

    url(r'^books/(?P<slug>[\w-]+)$', views.book_detail,
        name='book-detail'),

    url(r'^books/create/$', views.book_create, name='book-create'),

    url(r'^books/(?P<slug>[\w-]+)/checkout/$', views.book_checkout,
        name='book-checkout'),

    url(r'^books/(?P<slug>[\w-]+)/return/$', views.book_return,
        name='book-return'),

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
