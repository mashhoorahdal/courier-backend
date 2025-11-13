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
