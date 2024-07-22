from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PaymentViewSet,
    CreatePaymentSessionView,
    # stripe_webhook,
    PaymentSuccessView,
)

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payment")
router.register("stripe", PaymentSuccessView, basename="payment-success")

app_name = "payment"
urlpatterns = [
    path("", include(router.urls)),
    path(
        "create-session/<int:pk>/",
        CreatePaymentSessionView.as_view(),
        name="create-payment-session",
    ),
    # path("stripe-webhook/", stripe_webhook, name="stripe-webhook"),
    # path("success/", success_view, name="success"),
    # path("cancel/", cansel_view, name="cancel"),
]

urlpatterns += router.urls
