from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import register

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('', views.home, name='home'),
]
