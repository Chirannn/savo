from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    path('products/', views.admin_products_view, name='admin_products'),
    path('orders/', views.admin_orders_view, name='admin_orders'),
    path('orders/update-status/<int:order_id>/', views.update_order_status_view, name='update_order_status'),
]
