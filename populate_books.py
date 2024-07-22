import os
from decimal import Decimal

import django

# Налаштування Django оточення
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service_api.settings")
django.setup()

from book.models import Books

# Дані для заповнення
books_data = [
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": Decimal("1.50"),
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "cover": "SOFT",
        "inventory": 15,
        "daily_fee": Decimal("1.20"),
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "cover": "HARD",
        "inventory": 8,
        "daily_fee": Decimal("1.00"),
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "cover": "SOFT",
        "inventory": 12,
        "daily_fee": Decimal("1.30"),
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": Decimal("1.40"),
    },
    {
        "title": "Fahrenheit 451",
        "author": "Ray Bradbury",
        "cover": "SOFT",
        "inventory": 9,
        "daily_fee": Decimal("1.25"),
    },
    {
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "cover": "HARD",
        "inventory": 7,
        "daily_fee": Decimal("1.35"),
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "cover": "SOFT",
        "inventory": 10,
        "daily_fee": Decimal("1.10"),
    },
    {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "cover": "HARD",
        "inventory": 4,
        "daily_fee": Decimal("1.50"),
    },
    {
        "title": "Jane Eyre",
        "author": "Charlotte Brontë",
        "cover": "SOFT",
        "inventory": 11,
        "daily_fee": Decimal("1.20"),
    },
]

# Заповнення бази даних
for book_data in books_data:
    book, created = Books.objects.get_or_create(**book_data)
    if created:
        print(f"Додано книгу: {book.title} автор: {book.author}")
    else:
        print(f"Книга вже існує: {book.title} автор: {book.author}")
