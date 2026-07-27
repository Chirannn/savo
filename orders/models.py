from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from cart.models import Coupon
from decimal import Decimal
import uuid

class Order(models.Model):
    STATUS_CHOICES = (
        ('PLACED', 'Order Placed'),
        ('CONFIRMED', 'Order Confirmed'),
        ('PACKING', 'Packing Groceries'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('UPI', 'UPI Payment (GPay/PhonePe/Paytm)'),
        ('CARD', 'Credit / Debit Card'),
        ('COD', 'Cash on Delivery'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    delivery_slot = models.CharField(max_length=100, default='Standard Delivery (Today, within 2 hours)')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLACED')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    coupon_applied = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_note = models.CharField(max_length=255, default='Order received and sent to nearest Savo Mart dispatch store.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SAVO-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.full_name} ({self.get_order_status_display()})"

    @property
    def status_progress(self):
        mapping = {
            'PLACED': 20,
            'CONFIRMED': 40,
            'PACKING': 60,
            'OUT_FOR_DELIVERY': 85,
            'DELIVERED': 100,
            'CANCELLED': 0,
        }
        return mapping.get(self.order_status, 20)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_image = models.URLField(blank=True, null=True)
    unit = models.CharField(max_length=50, default='1 unit')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order.order_number}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - ₹{self.amount}"
