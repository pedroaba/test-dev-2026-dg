from django.contrib import messages
from django.shortcuts import redirect, render

from calculator.forms import CalculatorForm, ConsumerForm
from calculator.models import Consumer, DiscountRule
from calculator_python import calculator
from calculator.utils import get_consumption_range

# TODO: Your list view should do the following tasks
"""
-> Recover all consumers from the database
-> Get the discount value for each consumer
-> Calculate the economy
-> Send the data to the template that will be rendered
"""


def calculator_view(request):
    result = None
    selected_type = request.GET.get("type", "")
    selected_range = request.GET.get("range", "")
    consumers = Consumer.objects.select_related("discount_rule").order_by("name")

    if selected_type:
        consumers = consumers.filter(discount_rule__consumer_type=selected_type)

    if selected_range:
        consumers = consumers.filter(discount_rule__consumption_range=selected_range)

    if request.method == "POST":
        form = CalculatorForm(request.POST)
        if form.is_valid():
            values = form.cleaned_data

            consumption = [values["month_1"], values["month_2"], values["month_3"]]
            distributor_tax = values["distributor_tax"]
            tax_type = values["tax_type"]

            try:
                annual_savings, monthly_savings, applied_discount, coverage = calculator(
                    consumption,
                    distributor_tax,
                    tax_type,
                )
                result = {
                    "average_consumption": round(sum(consumption) / len(consumption), 2),
                    "annual_savings": annual_savings,
                    "monthly_savings": monthly_savings,
                    "applied_discount": round(applied_discount * 100, 2),
                    "coverage": round(coverage * 100, 2),
                }
            except Exception:
                form.add_error(
                    None,
                    "Nao foi possivel calcular a economia. Confira os dados e tente novamente.",
                )
    else:
        form = CalculatorForm()

    return render(
        request,
        "calculator/list.html",
        {
            "form": form,
            "result": result,
            "consumers": consumers,
            "selected_type": selected_type,
            "selected_range": selected_range,
        },
    )


# TODO: Your create view should do the following tasks
"""Create a view to perform inclusion of consumers. The view should do:
-> Receive a POST request with the data to register
-> If the data is valid (validate document), create and save a new Consumer object associated with the right discount rule object
-> Redirect to the template that list all consumers

Your view must be associated with an url and a template different from the first one. A link to
this page must be provided in the main page.
"""


def create_consumer_view(request):
    if request.method == "POST":
        form = ConsumerForm(request.POST)

        if form.is_valid():
            consumer = form.save(commit=False)
            tax_type = form.cleaned_data["tax_type"]
            consumer.discount_rule = DiscountRule.objects.get(
                consumer_type=tax_type,
                consumption_range=get_consumption_range(consumer.consumption),
            )
            consumer.save()
            messages.success(request, "Consumidor cadastrado com sucesso.")
            return redirect("calculator")
    else:
        form = ConsumerForm()

    return render(request, "calculator/create_consumer.html", {"form": form})
