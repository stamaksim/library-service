from django.utils import timezone
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payment.service import calculate_fine
from payment.views import CreatePaymentSessionView
from .models import Borrowing
from .serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    CreateBorrowingSerializer,
    BorrowingReturnSerializer,
)
from .telegram_utils import send_telegram_message


class BorrowingFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(method="filter_is_active")
    user_id = filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ["is_active", "user_id"]

    def filter_is_active(self, queryset, name, value):
        if value:
            return queryset.filter(actual_return_date__isnull=True)
        return queryset.exclude(actual_return_date__isnull=True)


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

    def perform_create(self, serializer):
        user = self.request.user
        active_borrowings = Borrowing.objects.filter(
            user=user, actual_return_date__isnull=True
        )

        if active_borrowings.exists():
            raise ValidationError(
                "You already have an active borrowing. Please return the current book before borrowing a new one."
            )
        instance = serializer.save()
        message = f"New borrowing created:\nUser: {instance.user.id}\nUser: {instance.user.email}\nBook: {instance.book.title}"
        result = send_telegram_message(message)
        if not result["success"]:
            print(f"Failed to send Telegram message: {result['message']}")

        payment_view = CreatePaymentSessionView.as_view()
        request = self.request._request
        response = payment_view(request, pk=instance.id)

        if response.status_code != 200:
            instance.delete()
            raise ValidationError("Failed to create Stripe payment session.")
        return instance

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(borrowing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(actual_return_date=timezone.now().date())

        fine = calculate_fine(borrowing)

        if fine > 0:
            payment_view = CreatePaymentSessionView.as_view()
            request_data_copy = request.data.copy()
            request_data_copy["fine"] = fine

            mutable_request = request._request
            mutable_request.POST = mutable_request.POST.copy()
            mutable_request.POST.update(request_data_copy)

            response = payment_view(mutable_request, pk=borrowing.id)

            if response.status_code != 200:
                raise ValidationError("Failed to create Stripe payment session.")

        return Response(serializer.data, status=status.HTTP_200_OK)
