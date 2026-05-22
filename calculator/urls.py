from django.urls import path

from calculator.views import calculator_view


urlpatterns = [
    path('', calculator_view, name='calculator'),
]
