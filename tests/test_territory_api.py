import pytest
from django.urls import reverse
from rest_framework import status

from payment_codes.models import Territory
from payment_codes.serializers import TerritorySerializer

pytestmark = pytest.mark.django_db


class TestTerritoryAPI:
    def test_list_territories(self, authenticated_client, territory):
        """Test retrieving a list of territories"""
        url = reverse("territory-list")
        response = authenticated_client.get(url)
        territories = Territory.objects.all()
        serializer = TerritorySerializer(territories, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_create_territory(self, authenticated_client):
        """Test creating a new territory"""
        url = reverse("territory-list")
        payload = {"name": "New Territory"}
        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Territory.objects.filter(name=payload["name"]).exists()

    def test_retrieve_territory(self, authenticated_client, territory):
        """Test retrieving a specific territory"""
        url = reverse("territory-detail", args=[territory.id])
        response = authenticated_client.get(url)
        serializer = TerritorySerializer(territory)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_update_territory(self, authenticated_client, territory):
        """Test updating a territory"""
        url = reverse("territory-detail", args=[territory.id])
        payload = {"name": "Updated Territory"}
        response = authenticated_client.put(url, payload)

        territory.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert territory.name == payload["name"]

    def test_partial_update_territory(self, authenticated_client, territory):
        """Test partially updating a territory"""
        url = reverse("territory-detail", args=[territory.id])
        payload = {"name": "Partially Updated Territory"}
        response = authenticated_client.patch(url, payload)

        territory.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert territory.name == payload["name"]

    def test_delete_territory(self, authenticated_client, territory):
        """Test deleting a territory"""
        url = reverse("territory-detail", args=[territory.id])
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Territory.objects.filter(id=territory.id).exists()

    def test_create_territory_invalid_data(self, authenticated_client):
        """Test creating a territory with invalid data"""
        url = reverse("territory-list")
        payload = {"name": ""}  # Empty name should be invalid
        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_territory_duplicate_name(self, authenticated_client, territory):
        """Test creating a territory with duplicate name"""
        url = reverse("territory-list")
        payload = {"name": territory.name}
        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthorized_access(self, api_client):
        """Test unauthorized access to territory endpoints"""
        url = reverse("territory-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
