from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from cart.models import Cart, Coupon
from cart.views import get_or_create_cart
from .models import Order, OrderItem, Payment
from accounts.models import Address
from decimal import Decimal
import uuid

def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty. Add groceries to proceed to checkout.")
        return redirect('product_list')

    # Coupon discount calculation
    coupon_code = request.session.get('coupon_code')
    coupon_discount = Decimal('0.00')
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code)
            if coupon_obj.is_valid(cart.subtotal):
                coupon_discount = coupon_obj.calculate_discount(cart.subtotal)
        except Coupon.DoesNotExist:
            pass

    grand_total = max(Decimal('0.00'), cart.grand_total - coupon_discount)

    addresses = []
    if request.user.is_authenticated:
        addresses = request.user.addresses.all()

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'coupon': coupon_obj,
        'coupon_discount': coupon_discount,
        'grand_total': grand_total,
        'addresses': addresses,
    }
    return render(request, 'orders/checkout.html', context)

def place_order_view(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        messages.error(request, "Cart is empty!")
        return redirect('product_list')

    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    street_address = request.POST.get('street_address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    postal_code = request.POST.get('postal_code')
    delivery_slot = request.POST.get('delivery_slot', 'Express Delivery (Within 2 Hours)')
    payment_method = request.POST.get('payment_method', 'UPI')

    # Calculate final numbers
    subtotal = cart.subtotal
    delivery_fee = cart.delivery_charge
    tax_amount = cart.tax

    coupon_code = request.session.get('coupon_code')
    discount_amount = Decimal('0.00')
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code)
            if coupon_obj.is_valid(subtotal):
                discount_amount = coupon_obj.calculate_discount(subtotal)
        except Coupon.DoesNotExist:
            pass

    grand_total = max(Decimal('0.00'), subtotal + delivery_fee + tax_amount - discount_amount)

    payment_status = 'PAID' if payment_method in ['UPI', 'CARD'] else 'PENDING'

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=street_address,
        city=city,
        state=state,
        postal_code=postal_code,
        delivery_slot=delivery_slot,
        payment_method=payment_method,
        payment_status=payment_status,
        order_status='PLACED',
        subtotal=subtotal,
        discount_amount=discount_amount,
        delivery_fee=delivery_fee,
        tax_amount=tax_amount,
        grand_total=grand_total,
        coupon_applied=coupon_obj,
        tracking_note='Order received by Savo Mart store. Preparing items for quality packaging.'
    )

    # Move cart items to order items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_image=item.product.image_url,
            unit=item.product.unit,
            price=item.unit_price,
            quantity=item.quantity,
            total_price=item.total_price
        )
        # Deduct stock
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.product.save()

    # Record Payment transaction
    transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
    Payment.objects.create(
        order=order,
        transaction_id=transaction_id,
        payment_method=payment_method,
        amount=grand_total,
        status='SUCCESS' if payment_status == 'PAID' else 'PENDING'
    )

    # Clear cart and session coupon
    cart.items.all().delete()
    if 'coupon_code' in request.session:
        del request.session['coupon_code']

    messages.success(request, f"Order #{order.order_number} placed successfully!")
    return redirect('order_confirmation', order_number=order.order_number)

def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/confirmation.html', {'order': order})

def order_tracking_search_view(request):
    query_order_number = request.GET.get('order_number', '').strip()
    if query_order_number:
        try:
            order = Order.objects.get(order_number__iexact=query_order_number)
            return redirect('order_tracking_detail', order_number=order.order_number)
        except Order.DoesNotExist:
            messages.error(request, f"Order number '{query_order_number}' not found. Please check and try again.")
    
    # Show recent user order if logged in
    latest_order = None
    if request.user.is_authenticated:
        latest_order = Order.objects.filter(user=request.user).first()

    return render(request, 'orders/tracking_search.html', {'latest_order': latest_order})

def order_tracking_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/tracking_detail.html', {'order': order})
