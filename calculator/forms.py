from decimal import Decimal

from django import forms

from calculator.models import Consumer, DiscountRule
from validate_docbr import CPF, CNPJ

from re import sub


class DecimalCommaFloatField(forms.FloatField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace(",", ".")

        return super().to_python(value)


class DecimalCommaDecimalField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace(",", ".")

        return super().to_python(value)


class CalculatorForm(forms.Form):
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
        cleaned_data = super().clean()

        document = cleaned_data.get("document")
        tax_type = cleaned_data.get("tax_type")

        if not document or not tax_type:
            return cleaned_data

        formatted_document = sub(r"\D", "", document)

        cpf_validator = CPF()
        cnpj_validator = CNPJ()

        if tax_type == DiscountRule.ConsumerType.RESIDENTIAL:
            if len(formatted_document) != 11 or not cpf_validator.validate(formatted_document):
                self.add_error(
                    "document",
                    "CPF inválido, por favor corrija e tente novamente.",
                )

        elif tax_type in [
            DiscountRule.ConsumerType.COMMERCIAL,
            DiscountRule.ConsumerType.INDUSTRIAL,
        ]:
            if len(formatted_document) != 14 or not cnpj_validator.validate(formatted_document):
                self.add_error(
                    "document",
                    "CNPJ inválido, por favor corrija e tente novamente.",
                )

        cleaned_data["document"] = formatted_document

        return cleaned_data
