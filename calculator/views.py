from django.shortcuts import render

from calculator.forms import CalculatorForm
from calculator_python import calculator

# TODO: Your list view should do the following tasks
"""
-> Recover all consumers from the database
-> Get the discount value for each consumer
-> Calculate the economy
-> Send the data to the template that will be rendered
"""


def calculator_view(request):
    result = None

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


def view2():
    # Create the second view here.
    pass
