
TRANSPORT_MONTHLY_KG = {
    "Car": 120,
    "Bike": 30,
    "Public Transport": 18,
    "Walking/Cycling": 0,
    "Electric Vehicle": 25,
}

ELECTRICITY_FACTOR = 0.45       # kg CO2e per kWh (global average grid mix)

FOOD_MONTHLY_KG = {
    "Non-Vegetarian": 55,
    "Vegetarian": 25,
    "Vegan": 15,
}

FLIGHT_KG_PER_FLIGHT = 250     # avg short-haul round-trip equivalent, monthly amortised

SHOPPING_MONTHLY_KG = {
    "High": 40,
    "Moderate": 20,
    "Low": 8,
}


def calculate_emission(
    transport: str,
    electricity: float,
    food: str,
    flights_per_year: int = 0,
    shopping: str = "Moderate",
) -> float:
    """
    Calculate estimated monthly carbon footprint in kg CO2e.

    Args:
        transport: Primary mode of transport.
        electricity: Monthly electricity consumption in kWh.
        food: Dietary habit category.
        flights_per_year: Number of flights taken per year.
        shopping: Shopping frequency/intensity level.

    Returns:
        Rounded monthly emission in kg CO2e.
    """
    transport_emission = TRANSPORT_MONTHLY_KG.get(transport, 0)
    electricity_emission = max(0, electricity) * ELECTRICITY_FACTOR
    food_emission = FOOD_MONTHLY_KG.get(food, 25)
    flight_emission = (flights_per_year * FLIGHT_KG_PER_FLIGHT) / 12
    shopping_emission = SHOPPING_MONTHLY_KG.get(shopping, 20)

    total = (
        transport_emission
        + electricity_emission
        + food_emission
        + flight_emission
        + shopping_emission
    )
    return round(total, 2)


def get_emission_breakdown(
    transport: str,
    electricity: float,
    food: str,
    flights_per_year: int = 0,
    shopping: str = "Moderate",
) -> dict:
    return {
        "Transport": TRANSPORT_MONTHLY_KG.get(transport, 0),
        "Electricity": round(max(0, electricity) * ELECTRICITY_FACTOR, 2),
        "Food": FOOD_MONTHLY_KG.get(food, 25),
        "Flights": round((flights_per_year * FLIGHT_KG_PER_FLIGHT) / 12, 2),
        "Shopping": SHOPPING_MONTHLY_KG.get(shopping, 20),
    }