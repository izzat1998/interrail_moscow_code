import pytest


from django.urls import reverse
from rest_framework import status
from payment_codes.models import Counterparty
from payment_codes.serializers import CounterpartySerializer

pytestmark = pytest.mark.django_db


class TestCounterpartyAPI:
    def test_list_counterparties(self, authenticated_client, counterparty):
        """Test retrieving a list of counterparties"""
        url = reverse("counterparty-list")
        response = authenticated_client.get(url)
        counterparties = Counterparty.objects.all()
        serializer = CounterpartySerializer(counterparties, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_create_counterparty(self, authenticated_client):
        """Test creating a new counterparty"""
        url = reverse("counterparty-list")
        payload = {"name": "New Counterparty"}
        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Counterparty.objects.filter(name=payload["name"]).exists()

    def test_retrieve_counterparty(self, authenticated_client, counterparty):
        """Test retrieving a specific counterparty"""
        url = reverse("counterparty-detail", args=[counterparty.id])
        response = authenticated_client.get(url)
        serializer = CounterpartySerializer(counterparty)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_update_counterparty(self, authenticated_client, counterparty):
        """Test updating a counterparty"""
        url = reverse("counterparty-detail", args=[counterparty.id])
        payload = {"name": "Updated Counterparty"}
        response = authenticated_client.put(url, payload)

        counterparty.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert counterparty.name == payload["name"]

    def test_partial_update_counterparty(self, authenticated_client, counterparty):
        """Test partially updating a counterparty"""
        url = reverse("counterparty-detail", args=[counterparty.id])
        payload = {"name": "Partially Updated Counterparty"}
        response = authenticated_client.patch(url, payload)

        counterparty.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert counterparty.name == payload["name"]

    def test_delete_counterparty(self, authenticated_client, counterparty):
        """Test deleting a counterparty"""
        url = reverse("counterparty-detail", args=[counterparty.id])
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Counterparty.objects.filter(id=counterparty.id).exists()

    def test_create_counterparty_invalid_data(self, authenticated_client):
        """Test creating a counterparty with invalid data"""
        url = reverse("counterparty-list")
        payload = {"name": ""}  # Empty name should be invalid
        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_counterparty_duplicate_name(
        self, authenticated_client, counterparty
    ):
        """Test creating a counterparty with duplicate name"""
        url = reverse("counterparty-list")
        payload = {"name": counterparty.name}
        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthorized_access(self, api_client):
        """Test unauthorized access to counterparty endpoints"""
        url = reverse("counterparty-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
