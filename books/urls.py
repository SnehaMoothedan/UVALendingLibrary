from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('provide/', views.provide_book_view, name='provide_page'),
    path('borrow/', views.borrow_books_view, name='borrow_page'),
    path('collection/create/', views.create_collection_view, name='create_collection_page'),
    path('collection/list/', views.list_collection_view, name='list_collection_page'),
    path('collection/<int:pk>/', views.collection_detail_view, name='collection_detail'),
    path('collection/<int:pk>/edit/', views.edit_collection_view, name='edit_collection'),
    path('collection/<int:pk>/delete/', views.delete_collection_view, name='delete_collection'),
    path('collections/my-collections/', views.list_my_collections_view, name='list_my_collections'),
    path('detail/<uuid:book_uuid>/', views.book_detail, name='book_detail'),
    path('request_borrow/<uuid:book_uuid>/', views.request_borrow_book, name='request_borrow_book'),
    path('delete-book/<uuid:book_uuid>/', views.delete_book_view, name='delete_book'),
    path('collection_access_request/<int:pk>/', collection_access_request_view, name='collection_access_request'),
    path('borrow_request/list/', views.list_borrow_request_view, name='list_borrow_request_page'),
    path('borrow_request/my_list/', views.list_my_borrow_request_view, name='list_my_borrow_request_page'),
    path('collection_request/list/', list_collection_request_view, name='list_collection_request_page'),
    path('collection_request/my_list/', list_my_collection_request_view, name='list_my_collection_request_page'),
    path('borrow_request/<int:request_id>/<str:action>/', views.handle_borrow_request_view, name='handle_borrow_request'),
    path('collection_request/<int:request_id>/<str:action>/', handle_collection_access_request_view, name='handle_collection_access_request'),
    path('review_borrower/<int:request_id>/', views.review_borrower, name='borrower_review'),
    path('my-books/', views.my_books_view, name='my_books'),
    path('borrow/<int:request_id>/review-book/', review_book_view, name='review_book'),
    path('books/<uuid:book_uuid>/reviews/', views.book_reviews_list, name='book_reviews_list'),
]