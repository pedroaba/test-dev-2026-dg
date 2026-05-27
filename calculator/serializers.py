"""Serializers used by calculator API endpoints."""

from rest_framework import serializers

from calculator.models import Consumer, DiscountRule
from calculator.utils import get_consumption_range, normalize_and_validate_document


class DiscountRuleSerializer(serializers.ModelSerializer):
    consumption_range_label = serializers.CharField(
        source="get_consumption_range_display",
        read_only=True,
    )

    class Meta:
        model = DiscountRule
        fields = [
            "id",
            "consumer_type",
            "consumption_range",
            "consumption_range_label",
            "discount",
            "coverage",
        ]


class CoverageRuleSerializer(serializers.ModelSerializer):
    consumption_range_label = serializers.CharField(
        source="get_consumption_range_display",
        read_only=True,
    )

    class Meta:
        model = DiscountRule
        fields = [
            "id",
            "consumer_type",
            "consumption_range",
            "consumption_range_label",
            "coverage",
        ]


class ConsumerSerializer(serializers.ModelSerializer):
    consumer_type = serializers.CharField(
        source="discount_rule.consumer_type",
        read_only=True,
    )
    coverage = serializers.DecimalField(
        source="discount_rule.coverage",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    discount = serializers.DecimalField(
        source="discount_rule.discount",
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Consumer
        fields = [
            "id",
            "name",
            "document",
            "zip_code",
            "city",
            "state",
            "consumption",
            "distributor_tax",
            "discount_rule",
            "consumer_type",
            "coverage",
            "discount",
        ]
        read_only_fields = ["discount_rule", "consumer_type", "coverage", "discount"]


class ConsumerUpdateSerializer(serializers.ModelSerializer):
    document = serializers.CharField(max_length=18, required=False)
    tax_type = serializers.ChoiceField(
        choices=DiscountRule.ConsumerType.choices,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Consumer
        fields = [
            "name",
            "document",
            "zip_code",
            "city",
            "state",
            "consumption",
            "distributor_tax",
            "tax_type",
        ]

    def validate_document(self, value):
        try:
            return normalize_and_validate_document(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate(self, attrs):
        instance = self.instance
        tax_type = attrs.get(
            "tax_type",
            getattr(getattr(instance, "discount_rule", None), "consumer_type", None),
        )
        consumption = attrs.get("consumption", getattr(instance, "consumption", None))

        if tax_type and consumption is not None:
            try:
                attrs["discount_rule"] = DiscountRule.objects.get(
                    consumer_type=tax_type,
                    consumption_range=get_consumption_range(consumption),
                )
            except DiscountRule.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"tax_type": "Regra de desconto não encontrada para o consumo informado."}
                ) from exc

        return attrs


class ConsumerImportRowSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    document = serializers.CharField(max_length=18)
    city = serializers.CharField(max_length=128)
    state = serializers.CharField(max_length=128)
    consumption = serializers.IntegerField(min_value=0)
    distributor_tax = serializers.DecimalField(
        max_digits=10,
        decimal_places=8,
        min_value=0,
    )
    tax_type = serializers.ChoiceField(
        choices=DiscountRule.ConsumerType.choices,
    )

    def validate_document(self, value):
        try:
            return normalize_and_validate_document(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate(self, attrs):
        tax_type = attrs["tax_type"]
        consumption = attrs["consumption"]

        try:
            attrs["discount_rule"] = DiscountRule.objects.get(
                consumer_type=tax_type,
                consumption_range=get_consumption_range(consumption),
            )
        except DiscountRule.DoesNotExist as exc:
            raise serializers.ValidationError(
                {"Tipo": "Regra de desconto não encontrada para o consumo informado."}
            ) from exc

        return attrs
