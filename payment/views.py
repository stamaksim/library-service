import stripe
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["GET"])
def payment_success(request):
    session_id = request.GET.get("session_id")
    try:
        payment = Payment.objects.get(session_id=session_id)

        if stripe.PaymentIntent.retrieve(payment.session_id).status == "succeeded":
            payment.status = Payment.Status.PAID
            payment.save()
            return Response({"status": "Payment successful"})
        else:
            return Response({"status": "Payment not successful"}, status=400)
    except Payment.DoesNotExist:
        return Response({"status": "Payment not found"}, status=404)


@api_view(["GET"])
def payment_cancel(request):
    return Response({"status": "Payment cancelled"})
