from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count
from orders.models import Order
from products.models import Product, Category
from decimal import Decimal

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.username == 'admin')

@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_dashboard_view(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    total_customers = User.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=10).count()
    
    recent_orders = Order.objects.all()[:10]
    recent_products = Product.objects.all()[:10]

    # Category breakdown for charts
    category_data = Category.objects.annotate(product_count=Count('products'))

    # Order status breakdown
    status_counts = {
        'PLACED': Order.objects.filter(order_status='PLACED').count(),
        'CONFIRMED': Order.objects.filter(order_status='CONFIRMED').count(),
        'PACKING': Order.objects.filter(order_status='PACKING').count(),
        'OUT_FOR_DELIVERY': Order.objects.filter(order_status='OUT_FOR_DELIVERY').count(),
        'DELIVERED': Order.objects.filter(order_status='DELIVERED').count(),
    }

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'category_data': category_data,
        'status_counts': status_counts,
    }
    return render(request, 'dashboard/index.html', context)

@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_products_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_product':
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            price = request.POST.get('price')
            discount_price = request.POST.get('discount_price') or None
            unit = request.POST.get('unit', '1 unit')
            stock = request.POST.get('stock', 50)
            image_url = request.POST.get('image_url')
            description = request.POST.get('description', '')
            category = get_object_or_404(Category, id=category_id)

            Product.objects.create(
                name=name,
                category=category,
                price=price,
                discount_price=discount_price,
                unit=unit,
                stock=stock,
                image_url=image_url,
                description=description
            )
            messages.success(request, f"Product '{name}' added successfully!")
            return redirect('admin_products')

    return render(request, 'dashboard/products.html', {'products': products, 'categories': categories})

@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_orders_view(request):
    orders = Order.objects.all()
    return render(request, 'dashboard/orders.html', {'orders': orders})

@user_passes_test(is_admin, login_url='/accounts/login/')
def update_order_status_view(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('order_status')
        tracking_note = request.POST.get('tracking_note', '')
        
        order.order_status = new_status
        if tracking_note:
            order.tracking_note = tracking_note
        if new_status == 'DELIVERED':
            order.payment_status = 'PAID'
        order.save()

        messages.success(request, f"Order {order.order_number} status updated to {order.get_order_status_display()}.")

    return redirect(request.META.get('HTTP_REFERER', 'admin_orders'))
