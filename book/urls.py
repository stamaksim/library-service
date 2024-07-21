from django.urls import path, include
from rest_framework import routers

from book.views import BookViewSet

router = routers.DefaultRouter()

app_name = "book"
router.register("", BookViewSet, basename="book")

urlpatterns = [path("", include(router.urls))]
