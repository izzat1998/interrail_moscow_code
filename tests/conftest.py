import os
import shutil
from datetime import date, datetime
from decimal import Decimal

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from payment_codes.models import Territory, Counterparty, Application, PaymentCode

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker, tmpdir_factory):
    """Set up test directories and template"""
    with django_db_blocker.unblock():
        # Create necessary directories
        media_root = settings.MEDIA_ROOT
        temp_dir = os.path.join(media_root, "temp")
        applications_dir = os.path.join(media_root, "test_applications")
        template_dir = os.path.join(
            settings.BASE_DIR, "test_templates", "test_documents"
        )

        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(applications_dir, exist_ok=True)
        os.makedirs(template_dir, exist_ok=True)

        # Create a dummy template file
        template_path = os.path.join(template_dir, "application_template.docx")
        if not os.path.exists(template_path):
            with open(template_path, "w") as f:
                f.write("Dummy template")

        yield

        # Cleanup after tests
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(applications_dir, ignore_errors=True)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def access_token(user):
    refresh = RefreshToken.for_user(user)
    return refresh.access_token


@pytest.fixture
def authenticated_client(api_client, access_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(access_token)}")
    return api_client


@pytest.fixture
def territory():
    return Territory.objects.create(name="Test Territory")


@pytest.fixture
def counterparty():
    return Counterparty.objects.create(name="Test Counterparty")


@pytest.fixture
def application(user, territory, counterparty):
    """Create a test application"""
    app = Application.objects.create(
        number="TEST001",
        sending_type="single",
        quantity=5,
        date=date(2024, 1, 1),
        forwarder=counterparty,
        departure="Moscow",
        departure_code="MSK",
        destination="St. Petersburg",
        destination_code="SPB",
        cargo="Test Cargo",
        hs_code="1234",
        etcng="5678",
        loading_type="wagon",
        weight=Decimal("1000.00"),
        container_type="20",
        conditions_of_carriage="Standard",
        agreed_rate=Decimal("500.00"),
        add_charges=Decimal("50.00"),
        manager=user,
        created=datetime.now(),
        modified=datetime.now(),
    )
    app.territories.add(territory)
    return app


@pytest.fixture
def payment_code(application, territory):
    """Create a test payment code"""
    return PaymentCode.objects.create(
        code_status="Checking",
        application=application,
        number="PC001",
        territory=territory,
        date=date(2024, 1, 1),
        weight="1000",
        rate=Decimal("500.00"),
        add_charges=Decimal("50.00"),
        created=datetime.now(),
        modified=datetime.now(),
    )
