from products.models import Category, Wishlist
from cart.models import Cart

def savo_mart_context(request):
    categories = Category.objects.all()
    cart_count = 0
    wishlist_count = 0

    # Cart count logic
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if hasattr(request.user, 'wishlist'):
            wishlist_count = request.user.wishlist.products.count()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()

    if cart:
        cart_count = cart.total_items

    return {
        'global_categories': categories,
        'global_cart_count': cart_count,
        'global_wishlist_count': wishlist_count,
    }
