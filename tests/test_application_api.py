from datetime import date
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from payment_codes.models import Application

pytestmark = pytest.mark.django_db


class TestApplicationCreateAPI:
    @patch("payment_codes.views.generate_application_document")
    @patch("payment_codes.utils.convert")
    def test_create_application(
        self,
        mock_convert,
        mock_generate_doc,
        authenticated_client,
        territory,
        counterparty,
    ):
        """Test creating a new application with mocked document generation"""
        # Setup mock returns
        mock_convert.return_value = "applications/test.pdf"
        mock_generate_doc.return_value = "applications/test.pdf"

        url = reverse("application-create")
        payload = {
            "number": "TEST002",
            "sending_type": "single",
            "quantity": 3,
            "date": "2024-01-01",
            "territories": [territory.id],
            "forwarder": counterparty.id,
            "departure": "Moscow",
            "departure_code": "MSK",
            "destination": "St. Petersburg",
            "destination_code": "SPB",
            "cargo": "Test Cargo",
            "loading_type": "wagon",
            "weight": "1000.00",
            "container_type": "20",
        }

        response = authenticated_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Application.objects.filter(number="TEST002").exists()

        # Verify mocks were called
        mock_generate_doc.assert_called_once()

        # Additional assertions
        created_application = Application.objects.get(number="TEST002")
        assert created_application.forwarder == counterparty
        assert territory in created_application.territories.all()
        assert created_application.date == date(2024, 1, 1)

    def test_create_application_invalid_data(self, authenticated_client):
        """Test creating an application with invalid data"""
        url = reverse("application-create")
        payload = {
            "number": "",  # Invalid empty number
            "quantity": -1,  # Invalid negative quantity
        }
        response = authenticated_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("payment_codes.views.generate_application_document")
    def test_create_application_doc_generation_failure(
        self, mock_generate_doc, authenticated_client, territory, counterparty
    ):
        """Test handling of document generation failure during application creation"""
        mock_generate_doc.side_effect = Exception("Document generation failed")

        url = reverse("application-create")
        payload = {
            "number": "TEST003",
            "sending_type": "single",
            "quantity": 3,
            "date": "2024-01-01",
            "territories": [territory.id],
            "forwarder": counterparty.id,
            "departure": "Moscow",
            "departure_code": "MSK",
        }

        response = authenticated_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Document generation failed" in str(response.data["error"])
        # Verify the application was not created
        assert not Application.objects.filter(number="TEST003").exists()

    # @patch("payment_codes.utils.generate_application_document")
    # def test_create_application_with_multiple_territories(
    #         self, mock_generate_doc, authenticated_client, territory, counterparty
    # ):
    #     """Test creating an application with multiple territories"""
    #     mock_generate_doc.return_value = "applications/test.pdf"
    #
    #     # Create a second territory
    #     second_territory = Territory.objects.create(name="Second Territory")
    #
    #     url = reverse("application-create")
    #     payload = {
    #         "number": "MULTI001",
    #         "sending_type": "single",
    #         "quantity": 2,
    #         "date": "2024-01-01",
    #         "territories": [territory.id, second_territory.id],
    #         "forwarder": counterparty.id,
    #         "departure": "City A",
    #         "destination": "City B",
    #     }
    #
    #     response = authenticated_client.post(url, payload, format="json")
    #
    #     assert response.status_code == status.HTTP_201_CREATED
    #     created_app = Application.objects.get(number="MULTI001")
    #     assert created_app.territories.count() == 2
    #     assert set(created_app.territories.values_list('id', flat=True)) == {
    #         territory.id,
    #         second_territory.id
    #     }


class TestApplicationUpdateAPI:
    @patch("payment_codes.views.generate_application_document")
    @patch("payment_codes.utils.convert")
    def test_update_application(
        self, mock_convert, mock_generate_doc, authenticated_client, application
    ):
        """Test updating an existing application"""
        mock_convert.return_value = "applications/updated_test.pdf"
        mock_generate_doc.return_value = "applications/updated_test.pdf"

        url = reverse("application-update", args=[application.id])
        payload = {
            "number": "TEST002-UPDATED",
            "sending_type": "block_train",
            "quantity": 4,
            "departure": "Updated Departure",
            "destination": "Updated Destination",
            "created": timezone.now(),
            "modified": timezone.now(),
            "forwarder": application.forwarder.id,
            "territories": [application.territories.first().id],
        }

        response = authenticated_client.put(url, payload, format="json")
        print("Response data:", response.data)
        assert response.status_code == status.HTTP_200_OK
        application.refresh_from_db()
        assert application.number == "TEST002-UPDATED"
        assert application.sending_type == "block_train"
        assert application.quantity == 4

        # Verify document generation was called
        mock_generate_doc.assert_called_once()

    @patch("payment_codes.views.generate_application_document")
    def test_update_application_doc_generation_failure(
        self, mock_generate_doc, authenticated_client, application
    ):
        """Test handling document generation failure during application update"""
        mock_generate_doc.side_effect = Exception("Document generation failed")

        url = reverse("application-update", args=[application.id])
        payload = {
            "number": "TEST002-UPDATED",
            "sending_type": "block_train",
            "quantity": 4,
            "departure": "Updated Departure",
            "destination": "Updated Destination",
            "created": timezone.now(),
            "modified": timezone.now(),
            "forwarder": application.forwarder.id,
            "territories": [application.territories.first().id],
        }

        response = authenticated_client.put(url, payload, format="json")
        print("Response data:", response.data)
        print("Response status code:", response.status_code)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Document generation failed" in str(response.data["error"])

        # Verify the application wasn't updated
        application.refresh_from_db()
        assert application.number != "TEST002-FAILED"

    def test_update_application_not_found(self, authenticated_client):
        """Test attempting to update a non-existent application"""
        url = reverse("application-update", args=[99999])
        payload = {"number": "TEST999"}

        response = authenticated_client.put(url, payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_application_details(
        self, authenticated_client, application, territory, payment_code
    ):
        """Test retrieving detailed application information"""
        url = reverse("application-detail", args=[application.id])
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["number"] == application.number
        assert response.data["sending_type"] == application.sending_type
        assert len(response.data["territories"]) == application.territories.count()
        assert len(response.data["codes"]) == 1
        assert response.data["codes"][0]["number"] == payment_code.number
