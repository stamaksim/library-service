from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from book.models import Books


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    def clean(self):
        if self.expected_return_date < self.actual_return_date:
            raise ValidationError(
                {
                    "expected_return_date": _(
                        "Expected return date cannot be earlier than borrow date."
                    )
                }
            )

        if self.actual_return_date:
            if self.actual_return_date < self.borrow_date:
                raise ValidationError(
                    {
                        "actual_return_date": _(
                            "Actual return date cannot be earlier than borrow date."
                        )
                    }
                )

            if self.actual_return_date > self.expected_return_date:
                raise ValidationError(
                    {
                        "actual_return_date": _(
                            "Actual return date cannot be later than expected return date."
                        )
                    }
                )

    @property
    def is_active(self):
        return self.actual_return_date is None
