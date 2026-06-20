
import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def get_ai_recommendations(user_context: dict) -> list[str]:
    """
    Generate AI-powered, personalized sustainability recommendations.

    Args:
        user_context: Dict with user lifestyle data and computed emission values.

    Returns:
        List of actionable recommendation strings.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if api_key:
        try:
            return _fetch_from_gemini(user_context, api_key)
        except Exception as e:
            logger.warning(f"Gemini API call failed, using fallback: {e}")

    return _rule_based_recommendations(user_context)


def _build_prompt(user_context: dict) -> str:
    return f"""You are Carbon Footprint Assistant, a helpful and encouraging sustainability assistant.
   

A user has submitted their lifestyle data:
- Primary transport: {user_context['transport']}
- Monthly electricity usage: {user_context['electricity_kwh']} kWh
- Dietary habit: {user_context['food']}
- Flights per year: {user_context['flights_per_year']}
- Shopping frequency: {user_context['shopping']}

Their estimated monthly carbon footprint is {user_context['emission_kg']} kg CO2e.
Their sustainability score is {user_context['score']}/100 and impact level is {user_context['category']}.

Generate exactly 5 specific, personalized, and actionable recommendations to help them reduce their carbon footprint.
Each recommendation should directly address their actual inputs — do not give generic advice.
Be encouraging, practical, and concise (1-2 sentences each).

Respond ONLY with a JSON array of 5 strings, no preamble, no markdown fences, no extra keys.
Example format: ["tip 1", "tip 2", "tip 3", "tip 4", "tip 5"]"""


def _fetch_from_gemini(user_context: dict, api_key: str) -> list[str]:
    """Call the Gemini API (free tier) to generate dynamic recommendations."""
    url = f"{GEMINI_API_URL}?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": _build_prompt(user_context)}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600,
        }
    }

    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()

    data = response.json()
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown fences if Gemini adds them
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    recommendations = json.loads(raw_text)
    if isinstance(recommendations, list) and len(recommendations) > 0:
        return [str(r) for r in recommendations[:5]]

    raise ValueError("Unexpected response structure from Gemini API.")


def _rule_based_recommendations(user_context: dict) -> list[str]:
    """Fallback rule-based recommendations when AI is unavailable."""
    tips = []
    transport = user_context.get("transport", "")
    electricity = user_context.get("electricity_kwh", 0)
    food = user_context.get("food", "")
    flights = user_context.get("flights_per_year", 0)
    shopping = user_context.get("shopping", "")

    if transport == "Car":
        tips.append("Switch to public transport or carpooling at least 3 days a week — this alone can cut your transport emissions by over 50%.")
    elif transport == "Bike":
        tips.append("Consider an electric bike for longer commutes to maintain your low-emission lifestyle while extending your range.")
    elif transport == "Electric Vehicle":
        tips.append("Great choice with an EV! Charging during off-peak hours and using renewable energy sources can further reduce your footprint.")
    elif transport == "Walking/Cycling":
        tips.append("Walking and cycling are the greenest options — you're already leading by example. Encourage others in your community to do the same.")
    else:
        tips.append("Public transport is a great choice! Even one fewer car trip per week makes a meaningful difference to your footprint.")

    if electricity > 150:
        tips.append(f"Your electricity usage of {electricity} kWh/month is high. Switching to LED lighting and a smart thermostat can cut usage by up to 30%.")
    elif electricity > 80:
        tips.append("Install a smart power strip and unplug idle devices — standby power can account for 10% of your electricity bill.")
    else:
        tips.append("Your electricity usage is already efficient! Consider enrolling in a green energy plan from your utility provider.")

    if food == "Non-Vegetarian":
        tips.append("Replacing red meat with plant-based proteins just 3 days a week can reduce your food-related emissions by up to 40%.")
    elif food == "Vegetarian":
        tips.append("Try incorporating one or two vegan days per week — dairy and eggs still carry a carbon cost, and reducing them helps.")
    else:
        tips.append("Your vegan diet is one of the most impactful choices for the planet — keep it up and inspire others around you!")

    if flights > 4:
        tips.append(f"You take {flights} flights/year, which significantly adds to your footprint. Consider train travel for shorter distances and video calls for business trips.")
    elif flights > 0:
        tips.append("For unavoidable flights, look into verified carbon offset programs and choose direct routes, which are more fuel-efficient.")
    else:
        tips.append("Avoiding flights is one of the highest-impact choices you can make — great work! Keep choosing ground transport where possible.")

    if shopping == "High":
        tips.append("High shopping frequency adds significant embedded carbon. Try a '30-day rule' — wait 30 days before non-essential purchases.")
    elif shopping == "Moderate":
        tips.append("When shopping, prioritize secondhand, locally made, or certified sustainable products to reduce embedded emissions.")
    else:
        tips.append("Your mindful approach to shopping is excellent! Share your habits with friends — social influence is one of the most powerful drivers of change.")

    return tips[:5]
