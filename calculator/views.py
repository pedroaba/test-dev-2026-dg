from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from calculator.forms import CalculatorForm, ConsumerForm
from calculator.models import Consumer, DiscountRule
from calculator.utils import get_consumption_range
from calculator_python import calculator
from core.views import CoreSystemBaseView


class HomeView(CoreSystemBaseView):
    page_name = "calculator"
    page_title = "Home"

    def get(self, request, *args, **kwargs):
        context = self.get_context(
            form=CalculatorForm(),
            result=None,
        )

        return render(
            request,
            "calculator/list.html",
            context,
        )

    def post(self, request, *args, **kwargs):
        result = None
        form = CalculatorForm(request.POST)

        if form.is_valid():
            values = form.cleaned_data
            consumption = [values["month_1"], values["month_2"], values["month_3"]]
            distributor_tax = values["distributor_tax"]
            tax_type = values["tax_type"]

            try:
                annual_savings, monthly_savings, applied_discount, coverage = (
                    calculator(
                        consumption,
                        distributor_tax,
                        tax_type,
                    )
                )
                result = {
                    "average_consumption": round(
                        sum(consumption) / len(consumption), 2
                    ),
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

        context = self.get_context(
            form=form,
            result=result,
        )

        return render(
            request,
            "calculator/list.html",
            context,
        )


class ConsumerListView(CoreSystemBaseView):
    page_name = "consumers"
    page_title = "Consumidores"

    table_headers = [
        "Nome",
        "Documento",
        "Consumo",
        "Tipo",
        "Cobertura",
        "Desconto",
        "Economia (Mensal)",
        "Economia (Anual)",
        "Acoes",
    ]

    def get_queryset(self, selected_type=None, selected_range=None):
        consumers = Consumer.objects.select_related("discount_rule").order_by("pk")

        if selected_type:
            consumers = consumers.filter(discount_rule__consumer_type=selected_type)

        if selected_range:
            consumers = consumers.filter(
                discount_rule__consumption_range=selected_range
            )

        return consumers

    @staticmethod
    def get_table_rows(consumers):
        rows = []

        for consumer in consumers:
            calculation = consumer.calculate
            rows.append(
                {
                    "cells": [
                        consumer.name,
                        consumer.document,
                        f"{consumer.consumption} kWh",
                        consumer.discount_rule.consumer_type,
                        f"{calculation['coverage']}%",
                        f"{calculation['discount']}%",
                        f"R$ {calculation['monthly_savings']}",
                        f"R$ {calculation['annual_savings']}",
                    ],
                    "buttons": [
                        {
                            "label": "Editar",
                            "action": "consumer_update",
                            "page": reverse(
                                "update_consumer",
                                kwargs={"pk": consumer.pk},
                            ),
                        },
                        {
                            "label": "Excluir",
                            "action": "consumer_delete",
                            "method": "DELETE",
                            "url": reverse(
                                "api_consumer_detail",
                                kwargs={"pk": consumer.pk},
                            ),
                        },
                    ],
                }
            )

        return rows

    def get(self, request, *args, **kwargs):
        selected_type = request.GET.get("type", "")
        selected_range = request.GET.get("range", "")
        consumers = self.get_queryset(selected_type, selected_range)

        context = self.get_context(
            table_headers=self.table_headers,
            table_rows=self.get_table_rows(consumers),
            empty_message="Nenhum consumidor encontrado.",
            table_label="Consumidores cadastrados",
            selected_type=selected_type,
            selected_range=selected_range,
        )

        return render(
            request,
            "calculator/consumers.html",
            context,
        )


class ConsumerCreateView(CoreSystemBaseView):
    page_title = "Criar Consumer"
    page_name = "create_consumer"

    @staticmethod
    def get_discount_rules():
        return DiscountRule.objects.order_by("consumer_type", "consumption_range")

    def get_context_data(self, form):
        return self.get_context(
            form=form,
            discount_rules=self.get_discount_rules(),
        )

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(ConsumerForm())

        return render(request, "calculator/create_consumer.html", context)

    def post(self, request, *args, **kwargs):
        form = ConsumerForm(request.POST)

        if form.is_valid():
            consumer = form.save(commit=False)
            tax_type = form.cleaned_data["tax_type"]

            # Discount rules are seeded by migration for every type/range pair.
            consumer.discount_rule = DiscountRule.objects.get(
                consumer_type=tax_type,
                consumption_range=get_consumption_range(consumer.consumption),
            )
            consumer.save()
            messages.success(request, "Consumidor cadastrado com sucesso.")
            return redirect(ConsumerListView.page_name)

        context = self.get_context_data(form)
        return render(request, "calculator/create_consumer.html", context)


class ConsumerUpdateView(CoreSystemBaseView):
    page_title = "Editar Consumer"
    page_name = "update_consumer"

    @staticmethod
    def get_discount_rules():
        return DiscountRule.objects.order_by("consumer_type", "consumption_range")

    @staticmethod
    def get_consumer(pk):
        return get_object_or_404(
            Consumer.objects.select_related("discount_rule"),
            pk=pk,
        )

    def get_form(self, consumer, data=None):
        initial = {}

        if consumer.discount_rule:
            initial["tax_type"] = consumer.discount_rule.consumer_type

        return ConsumerForm(data=data, instance=consumer, initial=initial)

    def get_context_data(self, form, consumer):
        return self.get_context(
            form=form,
            discount_rules=self.get_discount_rules(),
            form_title="Editar consumidor",
            form_eyebrow="Edicao",
            form_description="Atualize os dados do consumidor selecionado.",
            submit_label="Salvar alteracoes",
            form_api_url=reverse("api_consumer_detail", kwargs={"pk": consumer.pk}),
            form_api_method="PUT",
        )

    def get(self, request, pk, *args, **kwargs):
        consumer = self.get_consumer(pk)
        context = self.get_context_data(self.get_form(consumer), consumer)

        return render(request, "calculator/create_consumer.html", context)

    def post(self, request, pk, *args, **kwargs):
        consumer = self.get_consumer(pk)
        form = self.get_form(consumer, request.POST)

        if form.is_valid():
            updated_consumer = form.save(commit=False)
            tax_type = form.cleaned_data["tax_type"]
            updated_consumer.discount_rule = DiscountRule.objects.get(
                consumer_type=tax_type,
                consumption_range=get_consumption_range(updated_consumer.consumption),
            )
            updated_consumer.save()
            messages.success(request, "Consumidor atualizado com sucesso.")
            return redirect(ConsumerListView.page_name)

        context = self.get_context_data(form, consumer)
        return render(request, "calculator/create_consumer.html", context)
