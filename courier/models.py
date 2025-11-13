import uuid
from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    barcode = models.CharField(max_length=100, unique=True)
    receiver_name = models.CharField(max_length=100)
    receiver_address = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.barcode} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = self.generate_barcode()
        super().save(*args, **kwargs)

    def generate_barcode(self):
        """Generate a unique barcode for the order"""
        return f"CO-{uuid.uuid4().hex[:12].upper()}"

    def can_update_status(self, new_status):
        """Check if status transition is valid"""
        valid_transitions = {
            'pending': ['in_transit', 'cancelled'],
            'in_transit': ['delivered', 'cancelled'],
            'delivered': [],  # Final state
            'cancelled': []   # Final state
        }
        return new_status in valid_transitions.get(self.status, [])

    def update_status(self, new_status):
        """Update order status with validation"""
        if self.can_update_status(new_status):
            self.status = new_status
            self.save()
            return True
        return False

    def mark_as_paid(self):
        """Mark order as paid"""
        if self.payment_status == 'unpaid':
            self.payment_status = 'paid'
            self.save()
            return True
        return False

    def refund_payment(self):
        """Process refund"""
        if self.payment_status == 'paid':
            self.payment_status = 'refunded'
            self.save()
            return True
        return False

    @property
    def is_deliverable(self):
        """Check if order can be delivered"""
        return self.status in ['pending', 'in_transit'] and self.payment_status == 'paid'


class UserProfile(models.Model):
    """Extended user profile with roles"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('delivery_boy', 'Delivery Boy'),
        ('customer', 'Customer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_delivery_boy(self):
        return self.role == 'delivery_boy'

    @property
    def is_customer(self):
        return self.role == 'customer'


class DeliveryBoy(models.Model):
    """Delivery boy specific information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    vehicle_type = models.CharField(max_length=50, choices=[
        ('bike', 'Motorcycle'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ], blank=True)
    vehicle_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=20, blank=True)
    current_location = models.CharField(max_length=255, blank=True)
    is_available = models.BooleanField(default=True)
    total_deliveries = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.vehicle_type}"

    def update_delivery_count(self):
        """Update total deliveries count"""
        self.total_deliveries = self.deliveries.count()
        self.save()

    def calculate_rating(self):
        """Calculate average rating from deliveries"""
        ratings = [delivery.rating for delivery in self.deliveries.all() if delivery.rating]
        if ratings:
            self.rating = sum(ratings) / len(ratings)
            self.save()


class Delivery(models.Model):
    """Delivery assignments for delivery boys"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.CASCADE, related_name='deliveries')
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    customer_feedback = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.order.barcode} by {self.delivery_boy.user.username}"

    def mark_picked_up(self):
        """Mark delivery as picked up"""
        if self.status == 'assigned':
            self.status = 'picked_up'
            self.picked_up_at = models.DateTimeField(auto_now=True)
            self.save()
            return True
        return False

    def mark_delivered(self, rating=None, feedback=None):
        """Mark delivery as completed"""
        if self.status in ['picked_up', 'in_transit']:
            self.status = 'delivered'
            self.delivered_at = models.DateTimeField(auto_now=True)
            if rating:
                self.rating = rating
            if feedback:
                self.customer_feedback = feedback
            self.save()
            self.delivery_boy.update_delivery_count()
            self.delivery_boy.calculate_rating()
            return True
        return False
