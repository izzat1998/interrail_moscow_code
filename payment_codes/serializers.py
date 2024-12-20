from rest_framework import serializers, generics
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from payment_codes.models import Territory, Counterparty, Application, PaymentCode


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = "__all__"


class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("created", "modified", "request_file", "id", "manager")


class PaymentCodeSerializer(serializers.ModelSerializer):
    territory = TerritorySerializer()

    class Meta:
        model = PaymentCode
        fields = ["number", "territory", "id"]


class ApplicationRetrieveSerializer(serializers.ModelSerializer):
    codes = PaymentCodeSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("created", "modified", "request_file", "id", "manager")


class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # Automatically set the manager as the current user
        serializer.save(manager=self.request.user)


class ApplicationRetrieveView(generics.RetrieveAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationRetrieveSerializer
    permission_classes = [IsAuthenticated]


class PaymentCodeCreateSerializer(serializers.Serializer):
    start_range = serializers.CharField(required=True)
    end_range = serializers.CharField(required=True)
    territory_id = serializers.IntegerField(required=True)

    def validate_territory_id(self, value):
        """
        Check that the territory exists.
        """
        try:
            Territory.objects.get(id=value)
        except Territory.DoesNotExist:
            raise serializers.ValidationError("Territory does not exist.")
        return value

    # check for correct range
    def validate(self, data):
        """
        Check that the start range is less than or equal to the end range
        and that the range does not exceed the application's quantity.
        """
        start_range = data["start_range"]
        end_range = data["end_range"]
        application = self.context["view"].kwargs.get("pk")

        try:
            application = Application.objects.get(id=application)
        except Application.DoesNotExist:
            raise ValidationError({"error": "Application not found."})

        if start_range > end_range:
            raise ValidationError(
                {"error": "Start range must be less than or equal to end range."}
            )

        num_codes = int(end_range) - int(start_range) + 1
        total_allowed = application.territories.count() * application.quantity
        current_codes = application.codes.count()

        if num_codes + current_codes > total_allowed:
            raise ValidationError(
                {"error": "Range exceeds the application's quantity."}
            )

        return data
