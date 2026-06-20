# 🌿 Carbon Footprint Assistant

An AI-powered sustainability assistant that helps users estimate their carbon footprint, understand their environmental impact, and receive personalized recommendations for reducing emissions.

---

## Chosen Vertical

**Sustainability & Environmental Awareness**

---

## Problem Statement

Many people want to live more sustainably but do not know how their daily choices contribute to carbon emissions. Existing carbon calculators often provide only a number without meaningful guidance.

Carbon Footprint Assistant helps users estimate their monthly carbon footprint based on lifestyle choices and provides personalized recommendations using Google Gemini AI. When AI is unavailable, the application automatically falls back to a rule-based recommendation engine to ensure continuous functionality.

---

## Features

### Carbon Footprint Calculation

Calculates estimated monthly carbon emissions based on:

* Transportation method
* Electricity consumption
* Dietary habits
* Flights per year
* Shopping frequency

### Sustainability Score

Generates a sustainability score between 0 and 100 based on estimated emissions.

### Impact Classification

Categorizes users into:

* Low Impact
* Medium Impact
* High Impact

### AI-Powered Recommendations

Uses Google Gemini 1.5 Flash to generate personalized sustainability suggestions based on the user's lifestyle.

### Intelligent Fallback System

If Gemini is unavailable or no API key is configured, the application automatically generates contextual recommendations using a rule-based engine.

### Input Validation

Includes both client-side and server-side validation for reliable and secure operation.

### Responsive User Interface

Works across desktop and mobile devices.

### Automated Testing

Includes comprehensive unit and integration tests.

---

## Technology Stack

| Layer             | Technology                  |
| ----------------- | --------------------------- |
| Backend           | Python 3.11                 |
| Web Framework     | Flask 3.0                   |
| Frontend          | HTML5, CSS3, JavaScript     |
| AI                | Google Gemini 1.5 Flash API |
| Testing           | Pytest                      |
| Deployment        | Docker                      |
| Production Server | Gunicorn                    |

---

## How the Solution Works

### User Inputs

The user provides:

1. Transportation method
2. Monthly electricity consumption (kWh)
3. Dietary preference
4. Number of flights per year
5. Shopping frequency

### Carbon Emission Calculation

The application estimates monthly emissions using predefined emission factors.

Formula:

Monthly Emissions =
Transport +
(Electricity × Emission Factor) +
Food +
(Flights × Flight Factor ÷ 12) +
Shopping

### Sustainability Score

Score = max(0, min(100, 100 - (emission / 3)))

Higher scores indicate a more sustainable lifestyle.

### AI Recommendation Generation

The user's lifestyle information and calculated emissions are converted into a prompt and sent to Gemini 1.5 Flash.

Gemini generates five personalized sustainability recommendations.

### Fallback Recommendation Engine

If Gemini is unavailable:

* Transport-based recommendations
* Electricity reduction suggestions
* Food-related sustainability advice
* Travel recommendations
* Shopping behavior improvements

are generated automatically.

---

## Project Structure

carbon-footprint-assistant/

├── app.py

├── carbon_calculator.py

├── recommendation_engine.py

├── test_app.py

├── requirements.txt

├── Dockerfile

├── README.md

├── .env.example

├── .gitignore

├── templates/

│   └── index.html

└── static/

```
├── style.css

└── script.js
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/bhagyashree-goudar/carbon-footprint-assistant.git
cd carbon-footprint-assistant
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

You can obtain a free Gemini API key from Google AI Studio.

### Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8080
```

---

## Running Tests

Execute:

```bash
python -m pytest
```

Current Test Status:

* 24 Tests Passed
* Unit Tests
* Integration Tests
* Route Validation Tests
* Carbon Calculation Tests

---

## Security Considerations

* API keys are stored using environment variables.
* `.env` is excluded through `.gitignore`.
* User inputs are validated before processing.
* No personal data is stored.
* Application includes graceful fallback behavior if external AI services fail.

---

## Accessibility

The application incorporates:

* Semantic HTML elements
* Responsive design
* Accessible form labels
* Keyboard-friendly navigation
* Readable color contrast

---

## Assumptions

* Emission factors represent average estimates.
* User-provided values are assumed to be accurate.
* Calculations provide estimated monthly emissions rather than exact values.
* AI-generated recommendations depend on Gemini API availability.

---

## Future Enhancements

* User accounts and historical tracking
* Interactive charts and dashboards
* Country-specific emission factors
* Weekly sustainability reports
* Mobile application support
* Carbon offset integration

---

##Screenshots

![Home Page](home.png)

![Results](result.png)


---

## Repository

GitHub Repository:

https://github.com/bhagyashree-goudar/carbon-footprint-assistant

Deployed Link

https://carbon-footprint-assistant.onrender.com

---

Built as part of the PromptWars Virtual Challenge to promote sustainability awareness through AI-powered recommendations and practical environmental insights.

