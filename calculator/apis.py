"""HTTP API endpoints grouped by calculator app domain."""

import pandas as pd
from django.contrib import messages
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from calculator.models import Consumer, DiscountRule
from calculator.serializers import (
    ConsumerImportRowSerializer,
    ConsumerSerializer,
    ConsumerUpdateSerializer,
    CoverageRuleSerializer,
    DiscountRuleSerializer,
)


class DiscountRuleListAPIView(ListAPIView):
    """List discount rules registered in the system."""

    queryset = DiscountRule.objects.order_by("consumer_type", "consumption_range")
    serializer_class = DiscountRuleSerializer


class CoverageRuleListAPIView(ListAPIView):
    """List coverage rules registered in the system."""

    queryset = DiscountRule.objects.order_by("consumer_type", "consumption_range")
    serializer_class = CoverageRuleSerializer


class ConsumerBatchImportView(APIView):
    """Import consumers from an uploaded Excel spreadsheet."""

    parser_classes = [MultiPartParser, FormParser]

    @staticmethod
    def _error_response(request, payload):
        """Return redirect+messages for browser, JSON for API clients."""
        if "missing_columns" in payload:
            missing = ", ".join(payload["missing_columns"])
            messages.error(
                request,
                f"Arquivo invalido. Colunas ausentes: {missing}.",
            )
        elif "rows" in payload:
            messages.error(
                request,
                "Nao foi possivel importar a planilha. Corrija os dados e tente novamente.",
            )
            for row_error in payload["rows"][:5]:
                formatted_errors = ", ".join(
                    f"{field}: {', '.join(errors)}"
                    for field, errors in row_error["errors"].items()
                )
                messages.error(
                    request,
                    f"Linha {row_error['row']}: {formatted_errors}",
                )
        else:
            for field, errors in payload.items():
                if isinstance(errors, list):
                    messages.error(request, f"{field}: {', '.join(map(str, errors))}")
        return redirect("consumers")



    @extend_schema(
        summary="Import consumers from Excel",
        description=(
            "Uploads an Excel spreadsheet and imports or updates consumers. "
            "Expected columns: Nome, Documento, Cidade, Estado, Consumo(kWh), "
            "Tarifa da Distribuidora and Tipo."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "excel_file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Excel file with .xlsx or .xls extension.",
                    }
                },
                "required": ["excel_file"],
            }
        },
        responses={
            302: OpenApiResponse(description="Redirects to the consumers page."),
        },
    )
    def post(self, request):
        """Read the uploaded workbook and upsert one ``Consumer`` per row."""
        file = request.FILES.get("excel_file")
        if not file:
            return self._error_response(
                request,
                {"excel_file": ["Envie um arquivo Excel para importar."]},
            )
        df = pd.read_excel(file)
        required_columns = [
            "Nome",
            "Documento",
            "Cidade",
            "Estado",
            "Consumo(kWh)",
            "Tarifa da Distribuidora",
            "Tipo",
        ]
        missing_columns = [column for column in required_columns if column not in df.columns]

        if missing_columns:
            return self._error_response(
                request,
                {"missing_columns": missing_columns},
            )

        validated_rows = []
        row_errors = []

        for index, row in df.iterrows():
            serializer = ConsumerImportRowSerializer(
                data={
                    "name": row["Nome"],
                    "document": row["Documento"],
                    "city": row["Cidade"],
                    "state": row["Estado"],
                    "consumption": row["Consumo(kWh)"],
                    "distributor_tax": row["Tarifa da Distribuidora"],
                    "tax_type": row["Tipo"],
                }
            )

            if serializer.is_valid():
                validated_rows.append(serializer.validated_data)
            else:
                row_errors.append(
                    {
                        "row": int(index) + 2,
                        "errors": serializer.errors,
                    }
                )

        if row_errors:
            return self._error_response(request, {"rows": row_errors})

        for row in validated_rows:
            Consumer.objects.update_or_create(
                document=row["document"],
                defaults={
                    "name": row["name"],
                    "city": row["city"],
                    "state": row["state"],
                    "consumption": row["consumption"],
                    "distributor_tax": row["distributor_tax"],
                    "discount_rule": row["discount_rule"],
                },
            )

        messages.success(request, "Consumidores importados com sucesso.")
        return redirect("consumers")


class ConsumerAPIView(RetrieveUpdateDestroyAPIView):
    """Update or delete a consumer by id."""

    http_method_names = ["put", "patch", "delete", "options"]
    queryset = Consumer.objects.select_related("discount_rule")
    serializer_class = ConsumerUpdateSerializer

    @extend_schema(
        request=ConsumerUpdateSerializer,
        responses={200: ConsumerSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        request=ConsumerUpdateSerializer,
        responses={200: ConsumerSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ConsumerUpdateSerializer

        return ConsumerSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return Response(ConsumerSerializer(instance).data)
