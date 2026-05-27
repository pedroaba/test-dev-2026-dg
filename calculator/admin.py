"""Admin registrations for calculator domain models."""

from django.contrib import admin

from . import models

# Register both models so interview reviewers can inspect seeded rules and data.
admin.site.register(models.DiscountRule)
admin.site.register(models.Consumer)
