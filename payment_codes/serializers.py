from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
    
    def validate(self, data):
        loading_type = data.get("loading_type")
        container_type = data.get("container_type")
        weight = data.get("weight")
        
        # When loading_type is wagon, container_type should not be required and should be cleared
        if loading_type == "wagon":
            if not weight:
                raise serializers.ValidationError(
                    {"weight": "Weight is required when loading type is wagon."}
                )
            # Clear container_type for wagon loading
            data["container_type"] = ""
        
        # When loading_type is container, container_type should be required
        elif loading_type == "container":
            if not container_type:
                raise serializers.ValidationError(
                    {"container_type": "Container type is required when loading type is container."}
                )
        
        return data


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
