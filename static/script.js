// ── Emission factors ──────────────────────────────────────────────
const FACTORS = {
  car:        0.21,   // kg CO₂ per km
  bus:        0.089,  // kg CO₂ per km
  bike:       0.0,    // zero emissions
  electricity:0.233,  // kg CO₂ per kWh
  vegMeal:    0.5,    // kg CO₂ per meal
  nonVegMeal: 2.5,
 
};

// ── Persona-specific advice ───────────────────────────────────────
const PERSONA_TIPS = {
  student: [
    "Walk or cycle to campus when possible.",
    "Share rides with classmates to cut transport emissions.",
    "Opt for plant-based meals in the canteen.",
  ],
  office: [
    "Consider carpooling or public transport to work.",
    "Turn off office equipment when not in use.",
    "Bring a packed vegetarian lunch a few days a week.",
  ],
  remote: [
    "Optimise home heating/cooling to reduce electricity use.",
    "Batch errands to make fewer car trips.",
    "Join a local community garden for low-carbon produce.",
  ],
  other: [
    "Small daily swaps add up — try one meatless meal a day.",
    "Unplug chargers and appliances on standby.",
    "Choose public transport or cycling over driving when feasible.",
  ],
};

// ── Helpers ───────────────────────────────────────────────────────
function getVal(id) {
  return parseFloat(document.getElementById(id).value) || 0;
}

function saveToHistory(total) {
  const history = JSON.parse(localStorage.getItem("cfHistory") || "[]");
  history.unshift({ date: new Date().toLocaleDateString(), total: total.toFixed(2) });
  localStorage.setItem("cfHistory", JSON.stringify(history.slice(0, 7)));
}

function renderHistory() {
  const history = JSON.parse(localStorage.getItem("cfHistory") || "[]");
  const el = document.getElementById("history-output");
  if (history.length === 0) {
    el.innerHTML = "<li>No history yet.</li>";
    return;
  }
  el.innerHTML = history
    .map(h => `<li><strong>${h.date}</strong> — ${h.total} kg CO₂</li>`)
    .join("");
}

function getRating(total) {
  if (total < 5)  return { label: "Low 🟢",    msg: "Great job! Your footprint is well below average." };
  if (total < 12) return { label: "Medium 🟡",  msg: "Not bad — a few tweaks could make a real difference." };
  return            { label: "High 🔴",          msg: "Your footprint is high. Check the tips below to reduce it." };
}

// ── Main calculate handler ────────────────────────────────────────
function handleSubmit(e) {
  e.preventDefault();

  const carKm        = getVal("carKm");
  const busKm        = getVal("busKm");
  const bikeKm       = getVal("bikeKm");
  const electricity  = getVal("electricityKwh");
  const vegMeals     = getVal("vegMeals");
  const nonVegMeals  = getVal("nonVegMeals");
  const persona      = document.getElementById("persona").value;

  // Individual contributions
  const breakdown = {
    "Car travel":        carKm       * FACTORS.car,
    "Bus travel":        busKm       * FACTORS.bus,
    "Bike/Cycle":        bikeKm      * FACTORS.bike,
    "Electricity":       electricity * FACTORS.electricity,
    "Vegetarian meals":  vegMeals    * FACTORS.vegMeal,
    "Non-veg meals":     nonVegMeals * FACTORS.nonVegMeal,
  };

  const total = Object.values(breakdown).reduce((a, b) => a + b, 0);
  const rating = getRating(total);

  // ── Update total output ──
  document.getElementById("total-output").innerHTML =
    `Total: <strong>${total.toFixed(2)} kg CO₂</strong> today &nbsp;|&nbsp; ${rating.label}<br>
     <small>${rating.msg}</small>`;

  // ── Update breakdown list ──
  const breakdownEl = document.getElementById("breakdown-output");
  breakdownEl.innerHTML = Object.entries(breakdown)
    .filter(([, v]) => v > 0)
    .map(([label, val]) => `<li>${label}: <strong>${val.toFixed(3)} kg</strong></li>`)
    .join("") || "<li>No emissions entered.</li>";

  // ── Persona tips ──
  const tips = PERSONA_TIPS[persona] || PERSONA_TIPS.other;
  document.getElementById("advice-output").innerHTML =
    `<ul>${tips.map(t => `<li>${t}</li>`).join("")}</ul>`;

  // ── Save & render history ──
  saveToHistory(total);
  renderHistory();
}

// ── Init ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Fix: the HTML has a stray </form> before the fields; we attach to the button's
  // closest form, or fall back to the button itself.
  const form = document.getElementById("eco-form");
  if (form) {
    form.addEventListener("submit", handleSubmit);
  }
  renderHistory();
});s