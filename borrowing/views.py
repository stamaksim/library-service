from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Borrowing
from .serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    CreateBorrowingSerializer,
    BorrowingReturnSerializer,
)


class BorrowingFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(method="filter_is_active")
    user_id = filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ["is_active", "user_id"]

    def filter_is_active(self, queryset, name, value):
        if value:
            return queryset.filter(actual_return_data__isnull=True)
        return queryset.exclude(actual_return_data__isnull=True)


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = BorrowingFilter
    permission_classes_by_action = {
        "list": [IsAuthenticatedOrReadOnly],
        "retrieve": [IsAuthenticatedOrReadOnly],
        "create": [IsAuthenticated],
        "return_book": [IsAuthenticated],
    }

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "create":
            return CreateBorrowingSerializer
        elif self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingListSerializer

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Borrowing.objects.none()
        if user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user=user)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            borrowing.delete()
            return Response({"detail": "Book returned and borrowing record deleted"})
        return Response(serializer.errors, status=400)
