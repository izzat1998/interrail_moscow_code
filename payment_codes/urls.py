from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payment_codes.views import TerritoryViewSet, CounterpartyViewSet, ApplicationCreateView, ApplicationUpdateView, \
    ApplicationRetrieveView, PaymentCodeCreateRange

router = DefaultRouter()
router.register(r'territories', TerritoryViewSet)
router.register(r'counterparties', CounterpartyViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path("code_range/<int:pk>/create/", PaymentCodeCreateRange.as_view(), name='code-range-create'),
    path('application/create/', ApplicationCreateView.as_view(), name='application-create'),
    path('application/<int:pk>/update/', ApplicationUpdateView.as_view(), name='application-create'),
    path('application/<int:pk>/detail/', ApplicationRetrieveView.as_view(), name='application-detail'),

]
