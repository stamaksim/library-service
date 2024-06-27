from django.db import models


class Books(models.Model):
    class CoverType(models.TextChoices):
        HARD = "HARD", "Hard"
        SOFT = "SOFT", "Soft"

    title = models.CharField(max_length=56)
    author = models.CharField(max_length=56)
    cover = models.CharField(
        max_length=4, choices=CoverType.choices, default=CoverType.SOFT
    )
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["title"]

    def __str__(self):
        return self.title
