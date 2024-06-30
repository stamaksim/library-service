from django.utils import timezone
from rest_framework import serializers

from book.models import Books
from book.serializers import BookSerializer
from borrowing.models import Borrowing
from user.models import User


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(slug_field="title", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class CreateBorrowingSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Books.objects.all())

    class Meta:
        model = Borrowing
        fields = (
            "book",
            "expected_return_date",
        )

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory == 0:
            raise serializers.ValidationError(
                "This book is not available in the inventory."
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data.get("book")

        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(
            user=user,
            book=book,
            borrow_date=timezone.now(),
            expected_return_date=validated_data.get("expected_return_date"),
        )
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)

    def update(self, instance, validated_data):
        instance.actual_return_date = timezone.now().date()
        instance.save()

        instance.book.inventory += 1
        instance.book.save()

        return instance