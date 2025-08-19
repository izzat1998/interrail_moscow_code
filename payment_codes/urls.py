from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payment_codes.views import (
    TerritoryViewSet,
    CounterpartyViewSet,
    ApplicationCreateView,
    ApplicationUpdateView,
    ApplicationRetrieveView,
    PaymentCodeCreateRange,
    ApplicationListView,
)

router = DefaultRouter()
router.register(r"territories", TerritoryViewSet)
router.register(r"counterparties", CounterpartyViewSet)
urlpatterns = [
    path("", include(router.urls)),
    # InterRail Application endpoints
    path(
        "applications/",
        ApplicationListView.as_view(),
        name="interrail-applications-list",
    ),
    path(
        "applications/create/",
        ApplicationCreateView.as_view(),
        name="interrail-applications-create",
    ),
    path(
        "applications/<int:pk>/",
        ApplicationRetrieveView.as_view(),
        name="interrail-applications-detail",
    ),
    path(
        "applications/<int:pk>/update/",
        ApplicationUpdateView.as_view(),
        name="interrail-applications-update",
    ),
    # Payment Code endpoints
    path(
        "applications/<int:pk>/codes/create-range/",
        PaymentCodeCreateRange.as_view(),
        name="interrail-codes-create-range",
    ),
]
