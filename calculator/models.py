from decimal import Decimal

from django.db import models

from calculator_python import calculator


class DiscountRule(models.Model):
    COVERAGE_CHOICES = [
        (Decimal("90.00"), "90%"),
        (Decimal("95.00"), "95%"),
        (Decimal("99.00"), "99%"),
    ]

    class ConsumerType(models.TextChoices):
        RESIDENTIAL = "Residencial", "Residencial"
        COMMERCIAL = "Comercial", "Comercial"
        INDUSTRIAL = "Industrial", "Industrial"

    class ConsumptionRange(models.TextChoices):
        UNTIL_10000 = "until_10000", "< 10.000 kWh"
        BETWEEN_10000_AND_20000 = "between_10000_and_20000", ">= 10.000 kWh e <= 20.000 kWh"
        ABOVE_20000 = "above_20000", "> 20.000 kWh"

    consumer_type = models.CharField(
        "Tipo de Consumidor",
        max_length=32,
        choices=ConsumerType.choices,
    )
    consumption_range = models.CharField(
        "Faixa de Consumo",
        max_length=32,
        choices=ConsumptionRange.choices,
    )
    coverage = models.DecimalField(
        "Cobertura",
        max_digits=5,
        decimal_places=2,
        choices=COVERAGE_CHOICES,
        help_text="Percentual de cobertura. Exemplo: 90.00 para 90%",
    )
    discount = models.DecimalField(
        "Desconto",
        max_digits=5,
        decimal_places=2,
        help_text="Percentual de desconto. Exemplo: 18.00 para 18%",
    )

    class Meta:
        verbose_name = "Regra de Desconto"
        verbose_name_plural = "Regras de Desconto"

    def __str__(self):
        return f"{self.consumer_type} - {self.get_consumption_range_display()}"


class Consumer(models.Model):
    name = models.CharField("Nome do Consumidor", max_length=128)
    document = models.CharField("Documento(CPF/CNPJ)", max_length=14, unique=True)
    zip_code = models.CharField("CEP", max_length=8, null=True, blank=True)
    city = models.CharField("Cidade", max_length=128)
    state = models.CharField("Estado", max_length=128)
    consumption = models.IntegerField("Consumo(kWh)", blank=True, null=True)
    distributor_tax = models.DecimalField(
        "Tarifa da Distribuidora",
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
    )
    discount_rule = models.ForeignKey(
        DiscountRule,
        verbose_name="Regra de Desconto",
        on_delete=models.SET_NULL,
        related_name="consumers",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    @property
    def calculate(self):
        annual_savings, monthly_savings, discount, coverage = calculator(
            [self.consumption],
            float(str(self.distributor_tax)),
            self.discount_rule.consumer_type,
        )

        return {
            "annual_savings": annual_savings,
            "monthly_savings": monthly_savings,
            "discount": round(discount * 100),
            "coverage": round(coverage * 100),
        }
