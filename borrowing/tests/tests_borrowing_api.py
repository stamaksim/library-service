from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Books
from borrowing.models import Borrowing


class BorrowingModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.book = Books.objects.create(
            title="Test Book",
            author="Test Author",
            cover="SOFT",
            inventory=10,
            daily_fee=1.99,
        )

    def test_borrowing_creation(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertIsNone(borrowing.actual_return_date)
        self.assertTrue(borrowing.is_active)  # Змінено з False на True


class BorrowingApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.book = Books.objects.create(
            title="Test Book",
            author="Test Author",
            cover="SOFT",
            inventory=10,
            daily_fee=1.99,
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        payload = {
            "book": self.book.id,
            "expected_return_date": timezone.now().date() + timezone.timedelta(days=7),
        }
        response = self.client.post("/api/borrowing/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        borrowing = Borrowing.objects.get()
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(
            borrowing.user, self.user
        )  # Перевірка правильності користувача


class BorrowingApiReturnTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.book = Books.objects.create(
            title="Test Book",
            author="Test Author",
            cover="SOFT",
            inventory=10,
            daily_fee=1.99,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.client.force_authenticate(self.user)

    def test_return_book(self):
        payload = {"actual_return_date": timezone.now().date()}
        response = self.client.post(
            f"/api/borrowing/{self.borrowing.id}/return/", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.borrowing.actual_return_date, timezone.now().date())
