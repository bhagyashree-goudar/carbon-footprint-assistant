import os
from flask import Flask, render_template, request, jsonify
from carbon_calculator import calculate_emission
from recommendation_engine import get_ai_recommendations


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)


@app.route("/", methods=["GET"])
def home():
    """Render the main page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Accept user lifestyle inputs, compute carbon footprint,
    and return AI-generated personalized recommendations.
    """
    try:
        # --- Input extraction & validation ---
        transport = request.form.get("transport", "").strip()
        food = request.form.get("food", "").strip()
        shopping = request.form.get("shopping", "").strip()

        electricity_raw = request.form.get("electricity", "").strip()
        flights_raw = request.form.get("flights", "0").strip()

        valid_transport = ["Car", "Bike", "Public Transport", "Walking/Cycling", "Electric Vehicle"]
        valid_food = ["Non-Vegetarian", "Vegetarian", "Vegan"]
        valid_shopping = ["High", "Moderate", "Low"]

        errors = []
        if transport not in valid_transport:
            errors.append("Please select a valid transportation method.")
        if food not in valid_food:
            errors.append("Please select a valid food habit.")
        if shopping not in valid_shopping:
            errors.append("Please select a valid shopping frequency.")

        try:
            electricity = float(electricity_raw)
            if electricity < 0 or electricity > 10000:
                errors.append("Electricity usage must be between 0 and 10,000 kWh.")
        except ValueError:
            errors.append("Electricity usage must be a valid number.")
            electricity = 0

        try:
            flights = int(flights_raw)
            if flights < 0 or flights > 100:
                errors.append("Flights per year must be between 0 and 100.")
        except ValueError:
            errors.append("Flights per year must be a valid whole number.")
            flights = 0
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # --- Carbon calculation ---
        emission = calculate_emission(transport, electricity, food, flights, shopping)
        score = max(0, min(100, round(100 - (emission / 3), 1)))

        if emission < 80:
            category = "Low"
            category_color = "green"
        elif emission < 200:
            category = "Medium"
            category_color = "orange"
        else:
            category = "High"
            category_color = "red"

        # --- AI recommendations ---
        user_context = {
            "transport": transport,
            "electricity_kwh": electricity,
            "food": food,
            "flights_per_year": flights,
            "shopping": shopping,
            "emission_kg": emission,
            "category": category,
            "score": score,
        }
        recommendations = get_ai_recommendations(user_context)

        return jsonify({
            "success": True,
            "emission": emission,
            "score": score,
            "category": category,
            "category_color": category_color,
            "recommendations": recommendations,
        })

    except Exception as e:
        app.logger.error(f"Unexpected error in /analyze: {e}")
        return jsonify({"success": False, "errors": ["An unexpected error occurred. Please try again."]}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
