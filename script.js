const EMISSIONS = {
    carPerKm: 0.21,
    busPerKm: 0.08,
    bikePerKm: 0.0,
    electricityPerKWh: 0.7,
    vegMeal: 1.0,
    nonVegMeal: 3.0
  };
  
  const HISTORY_KEY = "carbonHistory";
  
  function getNumberValue(id) {
    const value = document.getElementById(id).value;
    const num = parseFloat(value);
    return isNaN(num) ? 0 : num;
  }
  
  function calculateEmissions(inputs) {
    const transport =
      inputs.carKm * EMISSIONS.carPerKm +
      inputs.busKm * EMISSIONS.busPerKm +
      inputs.bikeKm * EMISSIONS.bikePerKm;
  
    const energy = inputs.electricityKwh * EMISSIONS.electricityPerKWh;
  
    const food =
      inputs.vegMeals * EMISSIONS.vegMeal +
      inputs.nonVegMeals * EMISSIONS.nonVegMeal;
  
    const total = transport + energy + food;
  
    return {
      total,
      transport,
      energy,
      food
    };
  }
  
  function generateAdvice(persona, breakdown) {
    const { transport, energy, food, total } = breakdown;
  
    if (total === 0) {
      return "Enter some data to see where your emissions come from and get personalized tips.";
    }
  
    const transportShare = transport / total;
    const energyShare = energy / total;
    const foodShare = food / total;
  
    let advice = [];
  
    if (transportShare >= energyShare && transportShare >= foodShare) {
      advice.push("Most of your emissions come from transport. Try grouping trips, using public transport, or cycling for short distances.");
      if (persona === "student") {
        advice.push("As a student, you can reduce trips by planning classes and errands together and using college buses or shared rides.");
      } else if (persona === "office") {
        advice.push("As an office worker, consider carpooling with colleagues or taking bus/metro a few days a week.");
      }
    } else if (energyShare >= transportShare && energyShare >= foodShare) {
      advice.push("Home electricity seems to be your largest source. Turn off fans, lights, and AC when not needed, and use natural light in the daytime.");
    } else {
      advice.push("Food choices are a big part of your footprint. Try adding more vegetarian meals during the week.");
      advice.push("Even one or two meat-free days can reduce your emissions over time.");
    }
  
    if (total > 20) {
      advice.push("Your daily footprint is on the higher side. Start with one small change this week and track if your number goes down.");
    } else if (total > 5) {
      advice.push("Your footprint is moderate. Keep an eye on your largest category and experiment with small changes.");
    } else {
      advice.push("Nice! Your footprint for today is relatively low. Keep maintaining these habits.");
    }
  
    return advice.join(" ");
  }
  
  function loadHistory() {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    try {
      return JSON.parse(raw);
    } catch {
      return [];
    }
  }
  
  function saveTodayToHistory(total) {
    const history = loadHistory();
    const today = new Date().toISOString().slice(0, 10);
  
    const filtered = history.filter(entry => entry.date !== today);
    filtered.push({ date: today, total: Number(total.toFixed(2)) });
  
    filtered.sort((a, b) => a.date.localeCompare(b.date));
    const last7 = filtered.slice(-7);
  
    localStorage.setItem(HISTORY_KEY, JSON.stringify(last7));
  }
  
  function renderHistory() {
    const history = loadHistory();
    const ul = document.getElementById("history-output");
    ul.innerHTML = "";
  
    if (history.length === 0) {
      ul.textContent = "No history yet. Calculate at least one day to see trends.";
      return;
    }
  
    let sum = 0;
    history.forEach(entry => {
      sum += entry.total;
      const li = document.createElement("li");
      li.textContent = `${entry.date}: ${entry.total} kg CO₂`;
      ul.appendChild(li);
    });
  
    const avg = sum / history.length;
    const summary = document.createElement("li");
    summary.textContent = `Average over last ${history.length} days: ${avg.toFixed(2)} kg CO₂ per day`;
    ul.appendChild(summary);
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("activity-form");
    const totalOutput = document.getElementById("total-output");
    const breakdownOutput = document.getElementById("breakdown-output");
    const adviceOutput = document.getElementById("advice-output");
    const personaSelect = document.getElementById("persona");
  
    renderHistory();
  
    form.addEventListener("submit", (event) => {
      event.preventDefault();
  
      const inputs = {
        carKm: getNumberValue("carKm"),
        busKm: getNumberValue("busKm"),
        bikeKm: getNumberValue("bikeKm"),
        electricityKwh: getNumberValue("electricityKwh"),
        vegMeals: getNumberValue("vegMeals"),
        nonVegMeals: getNumberValue("nonVegMeals")
      };
  
      const breakdown = calculateEmissions(inputs);
      const persona = personaSelect.value;
  
      totalOutput.textContent = `Total for today: ${breakdown.total.toFixed(2)} kg CO₂`;
  
      breakdownOutput.innerHTML = "";
      const listItems = [
        `Transport: ${breakdown.transport.toFixed(2)} kg CO₂`,
        `Home energy: ${breakdown.energy.toFixed(2)} kg CO₂`,
        `Food: ${breakdown.food.toFixed(2)} kg CO₂`
      ];
  
      listItems.forEach(text => {
        const li = document.createElement("li");
        li.textContent = text;
        breakdownOutput.appendChild(li);
      });
  
      const advice = generateAdvice(persona, breakdown);
      adviceOutput.textContent = advice;
  
      saveTodayToHistory(breakdown.total);
      renderHistory();
    });
  });