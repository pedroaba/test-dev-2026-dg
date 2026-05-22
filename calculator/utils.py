from calculator.models import DiscountRule


def get_consumption_range(consumption):
    if consumption < 10000:
        return DiscountRule.ConsumptionRange.UNTIL_10000
    if consumption <= 20000:
        return DiscountRule.ConsumptionRange.BETWEEN_10000_AND_20000
    return DiscountRule.ConsumptionRange.ABOVE_20000