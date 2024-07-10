from django.conf import settings
from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        FINE = "FINE", "Fine"

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(max_length=15, choices=Type.choices, default=Type.PAYMENT)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="borrowing"
    )
    session = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )

    def __str__(self):
        return f"Payment {self.id}: {self.type} - {self.status}"
