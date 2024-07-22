from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from book.models import Books

BOOK_URL = reverse("book:book-list")


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": "SOFT",
        "inventory": 10,
        "daily_fee": 1.99,
    }
    defaults.update(params)
    return Books.objects.create(**defaults)


class PublicBookApiTest(TestCase):
    """
    Tests that anyone can view books.
    """

    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AdminBookApiTest(TestCase):
    """
    Tests that only admins can create, update, or delete books.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.test", password="adminpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 5,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Books.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_update_book(self):
        book = sample_book()
        payload = {"title": "Updated Title"}
        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, payload["title"])

    def test_delete_book(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Books.objects.filter(id=book.id).exists())


class NonAdminBookApiTest(TestCase):
    """
    Tests that non-admin users cannot create, update, or delete books.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.test", password="userpassword"
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 0.99,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        book = sample_book()
        payload = {"title": "Updated Title"}
        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
