from decimal import Decimal

from django import forms

from calculator.models import Consumer, DiscountRule
from calculator.utils import normalize_and_validate_document


class DecimalCommaFloatField(forms.FloatField):
    """Float field that accepts either comma or dot as decimal separator."""

    def to_python(self, value):
        """Normalize Brazilian decimal input before Django parses the value."""

        if isinstance(value, str):
            value = value.replace(",", ".")

        return super().to_python(value)


class DecimalCommaDecimalField(forms.DecimalField):
    """Decimal field that accepts Brazilian comma decimal notation."""

    def to_python(self, value):
        """Normalize the value while preserving ``DecimalField`` validation."""

        if isinstance(value, str):
            value = value.replace(",", ".")

        return super().to_python(value)


class CalculatorForm(forms.Form):
    """Input form for the ad-hoc savings calculator on the list page."""

    month_1 = DecimalCommaFloatField(
        label="Consumo do 1o mes",
        min_value=0,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 1518 kWh",
                "autocomplete": "off",
            }
        ),
    )
    month_2 = DecimalCommaFloatField(
        label="Consumo do 2o mes",
        min_value=0,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 1071 kWh",
                "autocomplete": "off",
            }
        ),
    )
    month_3 = DecimalCommaFloatField(
        label="Consumo do 3o mes",
        min_value=0,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 968 kWh",
                "autocomplete": "off",
            }
        ),
    )
    distributor_tax = DecimalCommaFloatField(
        label="Tarifa da distribuidora",
        min_value=0.01,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 0.95871974",
                "autocomplete": "off",
            }
        ),
    )
    tax_type = forms.ChoiceField(
        label="Tipo de tarifa",
        choices=DiscountRule.ConsumerType.choices,
        widget=forms.Select(attrs={"class": "input"}),
    )


class ConsumerForm(forms.ModelForm):
    """Registration form for consumers persisted in the database."""

    document = forms.CharField(label="Documento", max_length=18)
    distributor_tax = DecimalCommaDecimalField(
        label="Tarifa da distribuidora",
        min_value=Decimal("0.01"),
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 0.95871974",
            }
        ),
    )
    tax_type = forms.ChoiceField(
        label="Tipo de consumidor",
        choices=DiscountRule.ConsumerType.choices,
        widget=forms.Select(attrs={"class": "input"}),
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
        labels = {
            "name": "Nome",
            "document": "Documento",
            "zip_code": "CEP",
            "city": "Cidade",
            "state": "Estado",
            "consumption": "Consumo(kWh)",
            "distributor_tax": "Tarifa da distribuidora",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "document": forms.TextInput(
                attrs={
                    "class": "input",
                    "maxlength": "14",
                }
            ),
            "zip_code": forms.TextInput(
                attrs={
                    "class": "input",
                    "maxlength": "8",
                }
            ),
            "city": forms.TextInput(attrs={"class": "input", "readonly": "readonly"}),
            "state": forms.TextInput(attrs={"class": "input", "readonly": "readonly"}),
            "consumption": forms.NumberInput(attrs={"class": "input", "min": "0"}),
        }

    def clean(self):
        """Validate CPF/CNPJ and strip punctuation before saving."""

        cleaned_data = super().clean()

        document = cleaned_data.get("document")

        if not document:
            return cleaned_data

        try:
            cleaned_data["document"] = normalize_and_validate_document(document)
        except ValueError as exc:
            self.add_error("document", str(exc))

        return cleaned_data
