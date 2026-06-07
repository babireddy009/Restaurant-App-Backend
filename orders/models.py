from django.db import models
from django.conf import settings
from menu.models import MenuItem


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=20, default='', blank=True)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=50, default='online')  # 'online' or 'cod'
    is_paid = models.BooleanField(default=False)
    
    # Location Tracking
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', limit_choices_to={'role': 'driver'})
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lng = models.FloatField(null=True, blank=True)
    driver_lat = models.FloatField(null=True, blank=True)
    driver_lng = models.FloatField(null=True, blank=True)
    driver_name = models.CharField(max_length=100, blank=True, null=True) # Legacy
    driver_phone = models.CharField(max_length=20, blank=True, null=True) # Legacy
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=200)  # snapshot name
    item_price = models.DecimalField(max_digits=8, decimal_places=2)  # snapshot price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item_name}"

    @property
    def subtotal(self):
        return self.item_price * self.quantity


class ChatMessage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.CharField(max_length=50) # 'customer', 'driver', 'system'
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M')}] {self.sender} to Order #{self.order_id}: {self.message[:20]}"


class OrderReview(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    food_rating = models.PositiveSmallIntegerField(default=5)
    driver_rating = models.PositiveSmallIntegerField(default=5)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for Order #{self.order.id} by {self.user.username}"
