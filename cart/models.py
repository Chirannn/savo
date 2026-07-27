from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal
from django.utils import timezone

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def delivery_charge(self):
        # Free delivery for orders above ₹500
        if self.subtotal == 0:
            return Decimal('0.00')
        elif self.subtotal >= 500:
            return Decimal('0.00')
        return Decimal('40.00')

    @property
    def tax(self):
        # 5% GST calculation
        return round(self.subtotal * Decimal('0.05'), 2)

    @property
    def grand_total(self):
        return self.subtotal + self.delivery_charge + self.tax

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def unit_price(self):
        return self.product.effective_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text='Percentage e.g. 10.00')
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    def is_valid(self, subtotal):
        if not self.is_active:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        if Decimal(subtotal) < Decimal(self.min_order_amount):
            return False
        return True

    def calculate_discount(self, subtotal):
        if not self.is_valid(subtotal):
            return Decimal('0.00')
        discount = (Decimal(subtotal) * self.discount_percent) / Decimal('100.00')
        return min(discount, Decimal(self.max_discount))

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% OFF)"
