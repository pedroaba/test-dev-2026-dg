from django import forms


class DecimalCommaFloatField(forms.FloatField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace(",", ".")

        return super().to_python(value)


class CalculatorForm(forms.Form):
    month_1 = DecimalCommaFloatField(
        label="Consumo do 1o mes",
        min_value=0,
        error_messages={
            "invalid": "Informe um numero valido para o consumo do 1o mes.",
            "min_value": "O consumo do 1o mes nao pode ser negativo.",
            "required": "Informe o consumo do 1o mes.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 1518 kWh",
                "autocomplete": "off",
            }
        )
    )

    month_2 = DecimalCommaFloatField(
        label="Consumo do 2o mes",
        min_value=0,
        error_messages={
            "invalid": "Informe um numero valido para o consumo do 2o mes.",
            "min_value": "O consumo do 2o mes nao pode ser negativo.",
            "required": "Informe o consumo do 2o mes.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 1071 kWh",
                "autocomplete": "off",
            }
        )
    )

    month_3 = DecimalCommaFloatField(
        label="Consumo do 3o mes",
        min_value=0,
        error_messages={
            "invalid": "Informe um numero valido para o consumo do 3o mes.",
            "min_value": "O consumo do 3o mes nao pode ser negativo.",
            "required": "Informe o consumo do 3o mes.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 968 kWh",
                "autocomplete": "off",
            }
        )
    )

    distributor_tax = DecimalCommaFloatField(
        label="Tarifa da distribuidora",
        min_value=0.01,
        error_messages={
            "invalid": "Informe um numero valido para a tarifa da distribuidora.",
            "min_value": "A tarifa da distribuidora deve ser maior que zero.",
            "required": "Informe a tarifa da distribuidora.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Ex: 0.95871974",
                "autocomplete": "off",
            }
        )
    )

    tax_type = forms.ChoiceField(
        label="Tipo de tarifa",
        choices=[
            ("Residencial", "Residencial"),
            ("Comercial", "Comercial"),
            ("Industrial", "Industrial"),
        ],
        widget=forms.Select(
            attrs={
                "class": "input",
            }
        ),
    )
