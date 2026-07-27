from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('tracking/', views.order_tracking_search_view, name='order_tracking_search'),
    path('tracking/<str:order_number>/', views.order_tracking_detail_view, name='order_tracking_detail'),
]
