from django.contrib import admin
from django.urls import path, include
from allauth.account.views import LoginView

urlpatterns = [
   path('admin/', admin.site.urls),
   path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='account_login'),
   path('', include('accounts.urls')),
   path('books/', include('books.urls')),
   #path("chat/", include("chat.urls")),
]
