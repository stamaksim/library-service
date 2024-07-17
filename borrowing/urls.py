from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing.views import BorrowingViewSet

router = DefaultRouter()
router.register(r"", BorrowingViewSet, basename="borrowing")

app_name = "borrowing"

urlpatterns = [
    path("", include(router.urls)),
]
