from django.urls import path

from calculator.views import calculator_view, create_consumer_view
from calculator.apis import ConsumerBatchImportView


urlpatterns = [
    path('', calculator_view, name='calculator'),
    path('consumers/create/', create_consumer_view, name='create_consumer'),
    path(
        'api/v1/consumer/batch-import',
        ConsumerBatchImportView.as_view(),
        name='consumer_batch_import',
    ),
]
