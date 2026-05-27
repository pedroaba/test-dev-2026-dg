"""URL routes exposed by the calculator app."""

from django.urls import path

from calculator.apis import (
    ConsumerAPIView,
    ConsumerBatchImportView,
    CoverageRuleListAPIView,
    DiscountRuleListAPIView,
)
from calculator.views import (
    ConsumerCreateView,
    ConsumerListView,
    ConsumerUpdateView,
    HomeView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="calculator"),
    path("consumers/", ConsumerListView.as_view(), name="consumers"),
    path("consumers/create/", ConsumerCreateView.as_view(), name="create_consumer"),
    path(
        "consumers/<int:pk>/update/",
        ConsumerUpdateView.as_view(),
        name="update_consumer",
    ),
    path(
        "api/v1/discount/rules/",
        DiscountRuleListAPIView.as_view(),
        name="api_discount_rules",
    ),
    path(
        "api/v1/discount/coverages/",
        CoverageRuleListAPIView.as_view(),
        name="api_discount_coverages",
    ),
    path(
        "api/v1/consumer/batch-import",
        ConsumerBatchImportView.as_view(),
        name="consumer_batch_import",
    ),
    path(
        "api/v1/consumer/<int:pk>/",
        ConsumerAPIView.as_view(),
        name="api_consumer_detail",
    ),
]
