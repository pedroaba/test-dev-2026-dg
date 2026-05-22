from decimal import Decimal

import pandas as pd
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from calculator.models import Consumer, DiscountRule
from calculator_python import calculator
from calculator.utils import get_consumption_range


class ConsumerBatchImportView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES["excel_file"]
        df = pd.read_excel(file)

        for _, row in df.iterrows():
            consumption = int(row["Consumo(kWh)"])
            distributor_tax = Decimal(str(row["Tarifa da Distribuidora"]))
            tax_type = row["Tipo"]

            _, _, coverage, applied_discount = calculator(
                [consumption],
                float(distributor_tax),
                tax_type,
            )

            discount_rule = DiscountRule.objects.get(
                consumer_type=tax_type,
                consumption_range=get_consumption_range(consumption),
            )

            if discount_rule is None:
                discount_rule = DiscountRule.objects.create(
                    consumer_type=tax_type,
                    consumption_range=get_consumption_range(consumption),
                    discount=applied_discount,
                    coverage=coverage,
                )


            Consumer.objects.update_or_create(
                document=str(row["Documento"]),
                defaults={
                    "name": row["Nome"],
                    "city": row["Cidade"],
                    "state": row["Estado"],
                    "consumption": consumption,
                    "distributor_tax": distributor_tax,
                    "discount_rule": discount_rule,
                },
            )

        messages.success(request, "Consumidores importados com sucesso.")
        return redirect("calculator")
