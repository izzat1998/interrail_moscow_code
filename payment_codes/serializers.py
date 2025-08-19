from rest_framework import serializers, generics
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from core.models import Territory
from counterparty.models import Counterparty  
from payment_codes.models import InterrailRuApplication, InterrailRuCode


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = "__all__"


class CounterpartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Counterparty
        fields = "__all__"


class InterrailRuApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterrailRuApplication
        fields = "__all__"
        read_only_fields = ("created", "modified", "request_file", "id", "manager")


class InterrailRuApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterrailRuApplication
        fields = ["id"]
        read_only_fields = ["id"]


class InterrailRuCodeSerializer(serializers.ModelSerializer):
    territory = TerritorySerializer()

    class Meta:
        model = InterrailRuCode
        fields = ["number", "territory", "id"]


class InterrailRuApplicationRetrieveSerializer(serializers.ModelSerializer):
    ru_codes = InterrailRuCodeSerializer(many=True, read_only=True)

    class Meta:
        model = InterrailRuApplication
        fields = "__all__"
        read_only_fields = ("created", "modified", "request_file", "id", "manager")


class ApplicationCreateView(generics.CreateAPIView):
    queryset = InterrailRuApplication.objects.all()
    serializer_class = InterrailRuApplicationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # Automatically set the manager as the current user
        serializer.save(manager=self.request.user)


class ApplicationRetrieveView(generics.RetrieveAPIView):
    queryset = InterrailRuApplication.objects.all()
    serializer_class = InterrailRuApplicationRetrieveSerializer
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
            application = InterrailRuApplication.objects.get(id=application)
        except InterrailRuApplication.DoesNotExist:
            raise ValidationError({"error": "Application not found."})

        if start_range > end_range:
            raise ValidationError(
                {"error": "Start range must be less than or equal to end range."}
            )

        num_codes = int(end_range) - int(start_range) + 1
        total_allowed = application.territories.count() * application.quantity
        current_codes = application.ru_codes.count()

        if num_codes + current_codes > total_allowed:
            raise ValidationError(
                {"error": "Range exceeds the application's quantity."}
            )

        return data


# Backward compatibility aliases
ApplicationSerializer = InterrailRuApplicationSerializer
ApplicationListSerializer = InterrailRuApplicationListSerializer
PaymentCodeSerializer = InterrailRuCodeSerializer
ApplicationRetrieveSerializer = InterrailRuApplicationRetrieveSerializer
