from re import sub

from validate_docbr import CNPJ, CPF

from calculator.models import DiscountRule


def get_consumption_range(consumption):
    """Map a kWh consumption value to the matching ``DiscountRule`` range."""

    if consumption < 10000:
        return DiscountRule.ConsumptionRange.UNTIL_10000
    if consumption <= 20000:
        return DiscountRule.ConsumptionRange.BETWEEN_10000_AND_20000
    return DiscountRule.ConsumptionRange.ABOVE_20000


def normalize_and_validate_document(document=""):
    """Return only document digits when value is a valid CPF or CNPJ."""

    formatted_document = sub(r"\D", "", document)

    if CPF().validate(formatted_document) or CNPJ().validate(formatted_document):
        return formatted_document

    raise ValueError("Documento inválido. Informe um CPF ou CNPJ válido.")
