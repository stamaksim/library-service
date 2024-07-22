from django.db import models
from django.urls import reverse

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
    session = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="borrowing"
    )

    def __str__(self):
        return f"Payment {self.id}: {self.type} - {self.status}"

    def get_absolute_url(self):
        return reverse("payment-detail", args=[str(self.id)])
