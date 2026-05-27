"""Pure business rule used by the Django app and by the standalone checks."""


def calculator(consumption: list, distributor_tax: float, tax_type: str) -> tuple:
    """Calculate estimated energy savings for a consumer profile.

    Args:
        consumption: Monthly consumption values in kWh. The function uses the
            average of the provided months to choose the discount tier.
        distributor_tax: Distributor tariff applied to each covered kWh.
        tax_type: Consumer type. Expected values are ``Residencial``,
            ``Comercial`` or ``Industrial``.

    Returns:
        A tuple with ``annual_savings``, ``monthly_savings``,
        ``applied_discount`` and ``coverage``. Savings are rounded monetary
        values; discount and coverage are returned as decimal ratios.
    """
    annual_savings = 0
    monthly_savings = 0
    applied_discount = 0
    coverage = 0

    # Discount and coverage are tiered by average monthly consumption.
    mean_of_consumption = sum(consumption) / len(consumption)
    if mean_of_consumption < 10_000:
        coverage = 0.9
        if tax_type == "Residencial":
            applied_discount = 0.18
        elif tax_type == "Comercial":
            applied_discount = 0.16
        elif tax_type == "Industrial":
            applied_discount = 0.12
    elif mean_of_consumption >= 10_000 and mean_of_consumption <= 20_000:
        coverage = 0.95
        if tax_type == "Residencial":
            applied_discount = 0.22
        elif tax_type == "Comercial":
            applied_discount = 0.18
        elif tax_type == "Industrial":
            applied_discount = 0.15
    else:
        coverage = 0.99
        if tax_type == "Residencial":
            applied_discount = 0.25
        elif tax_type == "Comercial":
            applied_discount = 0.22
        elif tax_type == "Industrial":
            applied_discount = 0.18

    # Only the covered portion of consumption receives the negotiated discount.
    covered_consumption = mean_of_consumption * coverage
    covered_value = covered_consumption * distributor_tax

    monthly_savings = covered_value * applied_discount
    annual_savings = monthly_savings * 12

    return (
        round(annual_savings, 2),
        round(monthly_savings, 2),
        applied_discount,
        coverage,
    )


if __name__ == "__main__":
    # Lightweight executable regression checks for the challenge scenarios.
    print("Testing...")

    assert calculator([1518, 1071, 968], 0.95871974, "Industrial") == (
        1473.19,
        122.77,
        0.12,
        0.9,
    )

    assert calculator([1000, 1054, 1100], 1.12307169, "Residencial") == (
        2295.32,
        191.28,
        0.18,
        0.9,
    )

    assert calculator([973, 629, 726], 1.04820025, "Comercial") == (
        1405.56,
        117.13,
        0.16,
        0.9,
    )

    assert calculator([15000, 14000, 16000], 0.95871974, "Industrial") == (
        24591.16,
        2049.26,
        0.15,
        0.95,
    )

    assert calculator([12000, 11000, 11400], 1.12307169, "Residencial") == (
        32297.74,
        2691.48,
        0.22,
        0.95,
    )

    assert calculator([17500, 16000, 16400], 1.04820025, "Comercial") == (
        35776.75,
        2981.40,
        0.18,
        0.95,
    )

    assert calculator([30000, 29000, 29500], 0.95871974, "Industrial") == (
        60478.73,
        5039.89,
        0.18,
        0.99,
    )

    assert calculator([22000, 21000, 21400], 1.12307169, "Residencial") == (
        71602.56,
        5966.88,
        0.25,
        0.99,
    )

    assert calculator([25500, 23000, 21400], 1.04820025, "Comercial") == (
        63832.12,
        5319.34,
        0.22,
        0.99,
    )

    print("Everything passed")
