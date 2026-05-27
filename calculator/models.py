from decimal import Decimal

from django.db import models

from calculator_python import calculator


class DiscountRule(models.Model):
    """Discount and coverage rule for a consumer type and consumption range."""

    COVERAGE_CHOICES = [
        (Decimal("90.00"), "90%"),
        (Decimal("95.00"), "95%"),
        (Decimal("99.00"), "99%"),
    ]

    class ConsumerType(models.TextChoices):
        """Allowed customer categories used by forms, filters and imports."""

        RESIDENTIAL = "Residencial", "Residencial"
        COMMERCIAL = "Comercial", "Comercial"
        INDUSTRIAL = "Industrial", "Industrial"

    class ConsumptionRange(models.TextChoices):
        """Consumption bands that determine the applicable discount rule."""

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
        """Return a readable label for the Django admin and shell output."""

        return f"{self.consumer_type} - {self.get_consumption_range_display()}"


class Consumer(models.Model):
    """Consumer registered for savings calculation and spreadsheet imports."""

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
        """Return the consumer name in admin lists and query displays."""

        return self.name

    @property
    def calculate(self):
        """Return calculated savings for the consumer's stored consumption data.

        The template accesses this property for each table row, so it keeps the
        presentation-ready values grouped in a dictionary.
        """

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
