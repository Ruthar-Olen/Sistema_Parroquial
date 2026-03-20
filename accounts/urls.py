from django.urls import path
from django.contrib.auth import views as auth_views
from .views import redirect_user

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('redirect/', redirect_user, name='redirect_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]