import logging
import os

from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from payment_codes.models import Territory, Counterparty, Application, PaymentCode
from payment_codes.serializers import (
    TerritorySerializer,
    CounterpartySerializer,
    ApplicationSerializer,
    PaymentCodeCreateSerializer,
    ApplicationRetrieveSerializer,
)
from payment_codes.utils import generate_application_document

logger = logging.getLogger(__name__)


@extend_schema(tags=["Territories"])
class TerritoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing territories.
    """

    queryset = Territory.objects.all()
    serializer_class = TerritorySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List territories", description="Get a list of all territories"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create territory", description="Create a new territory", exclude=True
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve territory", description="Get details of a specific territory"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update territory",
        description="Update all fields of a specific territory",
        exclude=True,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update territory",
        description="Update one or more fields of a specific territory",
        exclude=True,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete territory",
        description="Delete a specific territory",
        exclude=True,
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Counterparties"])
class CounterpartyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing counterparties.
    """

    queryset = Counterparty.objects.all()
    serializer_class = CounterpartySerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List counterparties", description="Get a list of all counterparties"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create counterparty",
        description="Create a new counterparty",
        exclude=True,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve counterparty",
        description="Get details of a specific counterparty",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update counterparty",
        description="Update all fields of a specific counterparty",
        exclude=True,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update counterparty",
        description="Update one or more fields of a specific counterparty",
        exclude=True,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete counterparty",
        description="Delete a specific counterparty",
        exclude=True,
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Applications"])
@extend_schema(
    summary="Create a new application",
    description="""
    Creates a new application with the provided data.
    The system will automatically:
    - Assign the current user as manager
    - Generate a PDF document
    - Store the PDF path in request_file field

    Choice Fields:
    - sending_type: single (Одиночный) or block_train (КП)
    - loading_type: wagon (Вагон) or container (Контейнер)
    - container_type: 20, 20HC, 40, 40HC, 45

    Examples of valid data:
    - rolling_stock_1: Собственный (СПС) , Инвентарный (МПС)
    - rolling_stock_2: Платформа, Цистерна, Вагон , Фитинговая платформа
    - paid_telegram: true or false ('Прошу также предоставить проплатную телеграмму' if true else empty)
    - conditions_of_carriage: FOR-FOR,FOB-FOR ...
    """,
    responses={
        201: OpenApiResponse(
            description="Application created successfully",
            response=ApplicationSerializer,
        ),
        400: OpenApiResponse(
            description="Failed to create application due to validation errors or PDF generation failure"
        ),
    },
)
class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        instance = serializer.save(manager=self.request.user)
        try:
            # Generate PDF and update request_file field
            pdf_path = generate_application_document(instance)
            instance.request_file = pdf_path
            instance.save()
        except Exception as e:
            logger.error(
                f"Error generating PDF for application {instance.id}: {str(e)}"
            )
            instance.delete()  # Delete the application if document generation fails
            raise serializers.ValidationError(
                {"error": f"Failed to generate application document: {str(e)}"}
            )


@extend_schema(tags=["Applications"])
class ApplicationListView(generics.ListAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=["Applications"])
class ApplicationUpdateView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.instance
        # Store old file path if it exists
        old_file = instance.request_file.path if instance.request_file else None

        # Save the instance first
        instance = serializer.save()

        try:
            # Generate new PDF
            pdf_path = generate_application_document(instance)
            instance.request_file = pdf_path
            instance.save()

            # Delete old file if it exists
            if old_file and os.path.exists(old_file):
                os.remove(old_file)

        except Exception as e:
            logger.error(
                f"Error generating PDF for application {instance.id}: {str(e)}"
            )
            raise serializers.ValidationError(
                {"error": f"Failed to generate application document: {str(e)}"}
            )


@extend_schema(tags=["Applications"])
class ApplicationRetrieveView(generics.RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationRetrieveSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"


@extend_schema(tags=["Payment Codes"])
class PaymentCodeCreateRange(generics.CreateAPIView):
    serializer_class = PaymentCodeCreateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    @transaction.atomic
    def perform_create(self, serializer):
        pk = self.kwargs.get(self.lookup_field)
        data = serializer.validated_data
        start_range = data["start_range"]
        end_range = data["end_range"]
        territory_id = data["territory_id"]

        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            raise ValidationError({"error": "Application not found."})

        # Create the codes
        codes_to_create = []
        for number in range(int(start_range), int(end_range) + 1):
            codes_to_create.append(
                PaymentCode(
                    application=application,
                    date=application.date,
                    number=str(number).zfill(len(start_range)),
                    territory_id=territory_id,
                    created=timezone.now(),
                    modified=timezone.now(),
                )
            )

        # Bulk create for better performance
        PaymentCode.objects.bulk_create(codes_to_create)
