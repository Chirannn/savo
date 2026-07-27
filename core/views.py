from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product, Category

def home_view(request):
    featured_categories = Category.objects.filter(is_featured=True)[:6]
    best_sellers = Product.objects.filter(is_best_seller=True, is_active=True)[:8]
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    organic_deals = Product.objects.filter(is_organic=True, is_active=True)[:4]

    context = {
        'featured_categories': featured_categories,
        'best_sellers': best_sellers,
        'featured_products': featured_products,
        'organic_deals': organic_deals,
    }
    return render(request, 'core/home.html', context)

def about_view(request):
    return render(request, 'core/about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        messages.success(request, f"Thank you {name}! Your message regarding '{subject}' has been sent. We'll get back to you shortly.")
        return redirect('contact')
        
    return render(request, 'core/contact.html')
