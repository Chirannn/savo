from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Wishlist, Review

def product_list_view(request):
    products = Product.objects.filter(is_active=True)

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(short_description__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Organic filter
    if request.GET.get('organic') == 'true':
        products = products.filter(is_organic=True)

    # Rating filter
    min_rating = request.GET.get('rating')
    if min_rating:
        products = products.filter(rating__gte=min_rating)

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-review_count', '-rating')
    elif sort_by == 'discount':
        products = products.filter(discount_price__isnull=False).order_by('-price')
    else: # newest
        products = products.order_by('-created_at')

    categories = Category.objects.all()

    # User wishlist product IDs
    user_wishlist_ids = []
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        user_wishlist_ids = list(wishlist.products.values_list('id', flat=True))

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'user_wishlist_ids': user_wishlist_ids,
        'total_count': products.count(),
    }
    return render(request, 'products/list.html', context)

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    
    in_wishlist = False
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = wishlist.products.filter(id=product.id).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        title = request.POST.get('title', '')
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment
        )
        messages.success(request, 'Your review has been published!')
        return redirect('product_detail', slug=product.slug)

    context = {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
        'reviews': product.reviews.all()[:10],
    }
    return render(request, 'products/detail.html', context)

def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'products/categories.html', {'categories': categories})

def product_quickview_api(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = {
        'id': product.id,
        'name': product.name,
        'category': product.category.name,
        'price': str(product.price),
        'discount_price': str(product.discount_price) if product.discount_price else None,
        'effective_price': str(product.effective_price),
        'unit': product.unit,
        'image_url': product.image_url,
        'description': product.description,
        'short_description': product.short_description,
        'stock': product.stock,
        'rating': str(product.rating),
        'review_count': product.review_count,
        'discount_percent': product.discount_percent,
        'is_organic': product.is_organic,
    }
    return JsonResponse(data)

@login_required
def toggle_wishlist_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    
    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        added = False
        msg = f"Removed '{product.name}' from your wishlist."
    else:
        wishlist.products.add(product)
        added = True
        msg = f"Added '{product.name}' to your wishlist!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'added': added, 'message': msg, 'count': wishlist.products.count()})
    
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'accounts/wishlist.html', {'wishlist_products': wishlist.products.all()})
