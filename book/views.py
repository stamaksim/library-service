from rest_framework import viewsets

from book.models import Books
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
