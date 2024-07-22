from rest_framework import viewsets

from book.models import Books
from book.permission import IsAdminReadOnly
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminReadOnly]
