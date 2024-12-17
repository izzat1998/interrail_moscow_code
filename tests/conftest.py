import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from payment_codes.models import Territory, Counterparty

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def access_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token

@pytest.fixture
def authenticated_client(api_client, access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(access_token)}')
    return api_client

@pytest.fixture
def territory():
    return Territory.objects.create(name='Test Territory')

@pytest.fixture
def counterparty():
    return Counterparty.objects.create(name='Test Counterparty')