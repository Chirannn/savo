from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Address
from orders.models import Order
from products.models import Wishlist

def login_register_view(request):
    if request.user.is_authenticated:
        return redirect('user_profile')

    active_tab = request.GET.get('tab', 'login')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'home'
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
                active_tab = 'login'

        elif action == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')

            if password != password_confirm:
                messages.error(request, "Passwords do not match.")
                active_tab = 'register'
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken.")
                active_tab = 'register'
            elif User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                active_tab = 'register'
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                login(request, user)
                messages.success(request, f"Account created! Welcome to Savo Mart, {first_name or username}!")
                return redirect('home')

    return render(request, 'accounts/login_register.html', {'active_tab': active_tab})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

@login_required
def user_profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.phone = request.POST.get('phone', profile.phone)
        profile.default_address = request.POST.get('default_address', profile.default_address)
        profile.city = request.POST.get('city', profile.city)
        profile.state = request.POST.get('state', profile.state)
        profile.postal_code = request.POST.get('postal_code', profile.postal_code)
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')

    orders = Order.objects.filter(user=user)
    addresses = user.addresses.all()
    wishlist, _ = Wishlist.objects.get_or_create(user=user)

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'addresses': addresses,
        'wishlist_products': wishlist.products.all(),
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def add_address_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'HOME')
        recipient_name = request.POST.get('recipient_name')
        phone = request.POST.get('phone')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        is_default = request.POST.get('is_default') == 'on'

        Address.objects.create(
            user=request.user,
            title=title,
            recipient_name=recipient_name,
            phone=phone,
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            is_default=is_default
        )
        messages.success(request, "New address added successfully!")
    return redirect('user_profile')
