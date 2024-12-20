import pytest
from django.urls import reverse
from rest_framework import status
from payment_codes.models import PaymentCode
from django.utils import timezone

pytestmark = pytest.mark.django_db


class TestPaymentCodeAPI:
    def test_create_payment_code_range(
        self, authenticated_client, application, territory
    ):
        """Test creating a range of payment codes for an application"""
        url = reverse("code-range-create", args=[application.id])
        payload = {
            "start_range": "1001",
            "end_range": "1005",
            "territory_id": territory.id,
        }

        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        # Verify the correct number of codes were created
        codes = PaymentCode.objects.filter(application=application)
        assert codes.count() == 5

        # Verify the codes are sequential and properly formatted
        code_numbers = sorted([code.number for code in codes])
        expected_numbers = ["1001", "1002", "1003", "1004", "1005"]
        assert code_numbers == expected_numbers

        # Verify other fields are set correctly
        first_code = codes.first()
        assert first_code.territory_id == territory.id
        assert first_code.date == application.date
        assert first_code.code_status == PaymentCode.CODE_STATUS_CHOICES[0][0]

    def test_create_payment_code_range_exceeds_quantity(
        self, authenticated_client, application, territory
    ):
        """Test creating payment codes that exceed the application's quantity limit"""
        # Set application quantity
        application.quantity = 2
        application.save()

        url = reverse("code-range-create", args=[application.id])
        payload = {
            "start_range": "1001",
            "end_range": "1005",  # Trying to create 5 codes when only 2 are allowed
            "territory_id": territory.id,
        }

        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Range exceeds the application's quantity" in str(response.data["error"])
        # Verify no codes were created
        assert PaymentCode.objects.filter(application=application).count() == 0

    def test_create_payment_code_invalid_application(
        self, authenticated_client, territory
    ):
        """Test creating payment codes for non-existent application"""
        url = reverse("code-range-create", args=[99999])  # Non-existent application ID
        payload = {
            "start_range": "1001",
            "end_range": "1005",
            "territory_id": territory.id,
        }

        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Application not found" in str(response.data["error"])

    def test_create_payment_code_invalid_territory(
        self, authenticated_client, application
    ):
        """Test creating payment codes with non-existent territory"""
        url = reverse("code-range-create", args=[application.id])
        payload = {
            "start_range": "1001",
            "end_range": "1005",
            "territory_id": 99999,  # Non-existent territory ID
        }

        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_payment_code_invalid_range(
        self, authenticated_client, application, territory
    ):
        """Test creating payment codes with invalid range (end before start)"""
        url = reverse("code-range-create", args=[application.id])
        payload = {
            "start_range": "1005",
            "end_range": "1001",  # End range before start range
            "territory_id": territory.id,
        }

        response = authenticated_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Verify no codes were created
        assert PaymentCode.objects.filter(application=application).count() == 0

    def test_retrieve_application_with_codes(
        self, authenticated_client, application, territory
    ):
        """Test retrieving an application with its associated payment codes"""
        # Create some payment codes for the application
        PaymentCode.objects.create(
            application=application,
            number="1001",
            territory=territory,
            date=application.date,
            created=timezone.now(),
            modified=timezone.now(),
        )
        PaymentCode.objects.create(
            application=application,
            number="1002",
            territory=territory,
            date=application.date,
            created=timezone.now(),
            modified=timezone.now(),
        )

        url = reverse("application-detail", args=[application.id])
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["codes"]) == 2
        # Verify code details are included
        assert response.data["codes"][0]["number"] in ["1001", "1002"]
        assert response.data["codes"][1]["number"] in ["1001", "1002"]
        assert response.data["codes"][0]["territory"]["id"] == territory.id
