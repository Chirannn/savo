from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_register_view, name='login'),
    path('register/', views.login_register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('address/add/', views.add_address_view, name='add_address'),
]
