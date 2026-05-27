"""Django application configuration for the calculator app."""

from django.apps import AppConfig


class CalculatorConfig(AppConfig):
    """Default app config used by Django during startup."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "calculator"
