from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list_view, name='product_list'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('categories/', views.category_list_view, name='category_list'),
    path('api/quickview/<int:pk>/', views.product_quickview_api, name='product_quickview_api'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist_view, name='toggle_wishlist'),
]
