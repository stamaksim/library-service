from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet
from .views import payment_success, payment_cancel

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

app_name = "payment"

urlpatterns = [
    path("", include(router.urls)),
    path("payments/success/", payment_success, name="payment-success"),
    path("payments/cancel/", payment_cancel, name="payment-cancel"),
]
