# accounts/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    home,
    anonymous_view,
    choose_view,
    provide_view,
    profile_view,
    lending_policies_view,
    upload_picture_view,
    edit_profile_view,
    request_provider_view,
    manage_provider_requests_view,
    approve_provider_view,
    borrow_view,
    my_books_view,
    delete_book_view,
    edit_book_view,
)

urlpatterns = [
    path('', home, name='home'),
    path('books/', include('books.urls')),
    path('anonymous/', anonymous_view, name='anonymous'),
    path('accounts/', include('allauth.urls')),
    path('choose/', choose_view, name='choose'),
    path('provide/', provide_view, name='provide_page'),
    path('profile/', profile_view, name='profile'),
    path('upload-picture/', upload_picture_view, name='upload_picture'),
    path('policies/', lending_policies_view, name='lending_policies'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    #path('chat/', include("chat.urls", namespace='chat')),
    path('request-provider/', request_provider_view, name='request_provider'),
    path('manage-provider-requests/', manage_provider_requests_view, name='manage_provider_requests'),
    path('approve-provider/<int:user_id>/', approve_provider_view, name='approve_provider'),
    path('borrow/', borrow_view, name='borrow_page'),
    path('my-books/', my_books_view, name='my_books'),
    path('delete-book/<uuid:book_uuid>/', delete_book_view, name='delete_book'),
    path('edit-book/<uuid:book_uuid>/', edit_book_view, name='edit_book'),
]