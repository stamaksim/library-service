from rest_framework import serializers

from book.models import Books


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")
