import json
import pytest
from unittest.mock import patch, MagicMock
import os
from app import app
from carbon_calculator import calculate_emission, get_emission_breakdown
from recommendation_engine import _rule_based_recommendations, get_ai_recommendations


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Flask test client with testing config."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ─── Carbon Calculator Tests ─────────────────────────────────────────────────

class TestCarbonCalculator:

    def test_car_non_vegetarian_high_shopping(self):
        result = calculate_emission("Car", 100, "Non-Vegetarian", 0, "High")
        assert result > 0
        # Car(120) + Electricity(45) + Food(55) + Flights(0) + Shopping(40) = 260
        assert result == pytest.approx(260.0, abs=1.0)

    def test_walking_vegan_low_shopping(self):
        result = calculate_emission("Walking/Cycling", 50, "Vegan", 0, "Low")
        # Walking(0) + Electricity(22.5) + Food(15) + Flights(0) + Shopping(8) = 45.5
        assert result == pytest.approx(45.5, abs=1.0)

    def test_flights_contribution(self):
        without_flights = calculate_emission("Car", 100, "Vegetarian", 0, "Moderate")
        with_flights = calculate_emission("Car", 100, "Vegetarian", 12, "Moderate")
        # 12 flights * 250 / 12 = 250 extra per month
        assert with_flights > without_flights
        assert abs((with_flights - without_flights) - 250.0) < 1.0

    def test_zero_electricity(self):
        result = calculate_emission("Walking/Cycling", 0, "Vegan", 0, "Low")
        assert result >= 0

    def test_negative_electricity_clamped(self):
        """Negative electricity input should be treated as zero."""
        result = calculate_emission("Walking/Cycling", -50, "Vegan", 0, "Low")
        zero_result = calculate_emission("Walking/Cycling", 0, "Vegan", 0, "Low")
        assert result == zero_result

    def test_electric_vehicle(self):
        ev = calculate_emission("Electric Vehicle", 100, "Vegetarian", 0, "Moderate")
        car = calculate_emission("Car", 100, "Vegetarian", 0, "Moderate")
        assert ev < car

    def test_breakdown_keys(self):
        breakdown = get_emission_breakdown("Car", 100, "Non-Vegetarian", 4, "High")
        assert set(breakdown.keys()) == {"Transport", "Electricity", "Food", "Flights", "Shopping"}

    def test_breakdown_values_positive(self):
        breakdown = get_emission_breakdown("Car", 100, "Non-Vegetarian", 4, "High")
        for key, val in breakdown.items():
            assert val >= 0, f"{key} should be non-negative"

    def test_breakdown_sum_matches_total(self):
        transport, electricity, food, flights, shopping = "Car", 100, "Non-Vegetarian", 4, "High"
        total = calculate_emission(transport, electricity, food, flights, shopping)
        breakdown = get_emission_breakdown(transport, electricity, food, flights, shopping)
        assert abs(sum(breakdown.values()) - total) < 0.1


# ─── Recommendation Engine Tests ─────────────────────────────────────────────
class TestRecommendationEngine:

    def _ctx(self, transport="Car", electricity=150, food="Non-Vegetarian",
              flights=6, shopping="High", emission=300, category="High", score=30):
        return dict(transport=transport, electricity_kwh=electricity, food=food,
                    flights_per_year=flights, shopping=shopping,
                    emission_kg=emission, category=category, score=score)

    def test_returns_list(self):
        result = _rule_based_recommendations(self._ctx())
        assert isinstance(result, list)

    def test_returns_at_least_one_tip(self):
        result = _rule_based_recommendations(self._ctx())
        assert len(result) >= 1

    def test_max_five_tips(self):
        result = _rule_based_recommendations(self._ctx())
        assert len(result) <= 5

    def test_vegan_low_shopping_walking(self):
        ctx = self._ctx(transport="Walking/Cycling", food="Vegan",
                        flights=0, shopping="Low", emission=30, category="Low", score=90)
        result = _rule_based_recommendations(ctx)
        # Should still return tips, possibly encouraging ones
        assert len(result) >= 1

    def test_car_driver_gets_transport_tip(self):
        ctx = self._ctx(transport="Car")
        result = _rule_based_recommendations(ctx)
        combined = " ".join(result).lower()
        assert "transport" in combined or "carpool" in combined or "public" in combined

    def test_high_electricity_gets_energy_tip(self):
        ctx = self._ctx(electricity=300)
        result = _rule_based_recommendations(ctx)
        combined = " ".join(result).lower()
        assert "electricity" in combined or "energy" in combined or "led" in combined


# ─── Flask Route Tests ────────────────────────────────────────────────────────

class TestRoutes:

    def test_home_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_form(self, client):
        response = client.get("/")
        assert b"eco-form" in response.data

    def test_analyze_valid_input(self, client):
        data = {
            "transport": "Car",
            "electricity": "150",
            "food": "Non-Vegetarian",
            "flights": "2",
            "shopping": "Moderate",
        }
        response = client.post("/analyze", data=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["success"] is True
        assert result["emission"] > 0
        assert 0 <= result["score"] <= 100
        assert result["category"] in ["Low", "Medium", "High"]
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_analyze_missing_transport(self, client):
        data = {
            "electricity": "150",
            "food": "Vegetarian",
            "flights": "0",
            "shopping": "Low",
            }
        response = client.post("/analyze", data=data)
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_analyze_invalid_electricity(self, client):
        data = {
            "transport": "Car",
            "electricity": "not_a_number",
            "food": "Vegetarian",
            "flights": "0",
            "shopping": "Low",
        }
        response = client.post("/analyze", data=data)
        assert response.status_code == 400

    def test_analyze_negative_electricity(self, client):
        data = {
            "transport": "Car",
            "electricity": "-100",
            "food": "Vegetarian",
            "flights": "0",
            "shopping": "Low",
        }
        response = client.post("/analyze", data=data)
        assert response.status_code == 400

    def test_analyze_invalid_food(self, client):
        data = {
            "transport": "Car",
            "electricity": "100",
            "food": "Pescatarian",   # not a valid option
            "flights": "0",
            "shopping": "Moderate",
        }
        response = client.post("/analyze", data=data)
        assert response.status_code == 400

    def test_analyze_vegan_walking_low_impact(self, client):
        data = {
            "transport": "Walking/Cycling",
            "electricity": "30",
            "food": "Vegan",
            "flights": "0",
            "shopping": "Low",
        }
        response = client.post("/analyze", data=data)
        result = json.loads(response.data)
        assert result["success"] is True
        assert result["category"] == "Low"

    def test_analyze_category_high(self, client):
        data = {
            "transport": "Car",
            "electricity": "500",
            "food": "Non-Vegetarian",
            "flights": "20",
            "shopping": "High",
        }
        response = client.post("/analyze", data=data)
        result = json.loads(response.data)
        assert result["success"] is True
        assert result["category"] == "High"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
