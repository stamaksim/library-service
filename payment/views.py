import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.service import calculate_total_price

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(borrowing__user=user)

    def perform_create(self, serializer):
        borrowing = serializer.validated_data.get("borrowing")
        if borrowing.user != self.request.user:
            raise ValidationError(
                "You do not have permission to create this payment session."
            )
        serializer.save(user=self.request.user)


class CreatePaymentSessionView(APIView):
    def post(self, request, pk):
        borrowing = get_object_or_404(Borrowing, pk=pk)
        money_to_pay = calculate_total_price(borrowing)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Payment for Borrowing {borrowing.id}",
                            },
                            "unit_amount": int(money_to_pay * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="http://localhost:8000/api/payment/stripe/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:8000/api/payment/stripe/cancel/?session_id={CHECKOUT_SESSION_ID}",
            )

            payment = Payment.objects.create(
                status=Payment.Status.PENDING,
                type=Payment.Type.PAYMENT,
                session=checkout_session.url,
                session_id=checkout_session.id,
                money_to_pay=money_to_pay,
                borrowing=borrowing,
            )

            return Response({"session_id": checkout_session.id})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def complete_payment(payment_id):
    payment = Payment.objects.get(id=payment_id)
    session_id = payment.session_id

    try:
        stripe.PaymentIntent.confirm(session_id)
        payment.status = Payment.Status.PAID
        payment.save()

        return True, "Payment completed successfully"
    except stripe.error.StripeError as e:
        return False, str(e)


class PaymentSuccessView(ViewSet):

    @action(
        detail=False,
        methods=["get"],
        url_path="success",
        authentication_classes=[],
        permission_classes=[AllowAny],
    )
    def success(self, request):
        session_id = request.query_params.get("session_id")

        payment = Payment.objects.filter(session_id=session_id).first()
        if not payment:
            return Response(
                "Payment session not found", status=status.HTTP_404_NOT_FOUND
            )
        if payment.status == Payment.Status.PAID:
            return Response(
                "Payment is already paid", status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = Payment.Status.PAID
        payment.save()
        return Response(
            "Payment was successful. Status updated to PAID.", status=status.HTTP_200_OK
        )

    @action(
        detail=False, methods=["get"], url_path="cancel", permission_classes=[AllowAny]
    )
    def cancel(self, request):
        return Response("Payment was canceled", status=status.HTTP_200_OK)
