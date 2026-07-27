from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem, Coupon

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_detail_view(request):
    cart = get_or_create_cart(request)
    coupon_code = request.session.get('coupon_code')
    coupon_discount = 0
    coupon_obj = None

    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code)
            if coupon_obj.is_valid(cart.subtotal):
                coupon_discount = float(coupon_obj.calculate_discount(cart.subtotal))
            else:
                del request.session['coupon_code']
                messages.warning(request, "Coupon is no longer valid for this cart subtotal.")
        except Coupon.DoesNotExist:
            del request.session['coupon_code']

    grand_total = max(0, float(cart.grand_total) - coupon_discount)

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'coupon': coupon_obj,
        'coupon_discount': coupon_discount,
        'grand_total': grand_total,
    }
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    msg = f"Added {product.name} ({product.unit}) to your cart!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart_count': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })

    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'cart_detail'))

@require_POST
def update_cart_item_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    cart = cart_item.cart

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': str(cart_item.total_price) if quantity > 0 else '0.00',
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
            'delivery_charge': str(cart.delivery_charge),
            'tax': str(cart.tax),
            'grand_total': str(cart.grand_total)
        })

    return redirect('cart_detail')

@require_POST
def remove_cart_item_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name
    cart = cart_item.cart
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"Removed {product_name} from cart.",
            'cart_count': cart.total_items,
            'subtotal': str(cart.subtotal),
            'delivery_charge': str(cart.delivery_charge),
            'tax': str(cart.tax),
            'grand_total': str(cart.grand_total)
        })

    messages.success(request, f"Removed {product_name} from cart.")
    return redirect('cart_detail')

@require_POST
def apply_coupon_view(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = get_or_create_cart(request)

    try:
        coupon = Coupon.objects.get(code=code)
        if coupon.is_valid(cart.subtotal):
            request.session['coupon_code'] = coupon.code
            messages.success(request, f"Coupon '{code}' applied! You saved {coupon.discount_percent}%!")
        else:
            messages.error(request, f"Coupon '{code}' requires a minimum order of ₹{coupon.min_order_amount}.")
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")

    return redirect('cart_detail')
