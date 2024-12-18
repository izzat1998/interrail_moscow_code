from datetime import date
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from payment_codes.models import Application

pytestmark = pytest.mark.django_db


class TestApplicationAPI:
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
