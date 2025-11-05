const expressionEl = document.getElementById("expression");
const resultEl = document.getElementById("result");
const keys = document.querySelectorAll(".key");
const display = document.querySelector(".display");
const glowToggle = document.getElementById("glowToggle");

let currentExpression = "";
let currentResult = "0";
let lastKeyType = "number";

function updateDisplay() {
  expressionEl.textContent = currentExpression || "0";
  resultEl.textContent = currentResult;
  display.classList.add("active");
  setTimeout(() => display.classList.remove("active"), 200);
}

function computeExpression(expr) {
  try {
    // eslint-disable-next-line no-eval
    const value = eval(expr.replace(/÷/g, "/").replace(/×/g, "*"));
    if (Number.isFinite(value)) {
      return parseFloat(value.toFixed(8)).toString();
    }
    return "0";
  } catch (error) {
    return "0";
  }
}

function appendValue(value) {
  if (value === ".") {
    const lastNumber = currentExpression.split(/[-+×÷]/).pop();
    if (lastNumber.includes(".")) return;
    if (!lastNumber) {
      currentExpression += "0";
    }
  }

  if (currentExpression === "0" && value !== ".") {
    currentExpression = value;
  } else {
    currentExpression += value;
  }

  currentResult = computeExpression(currentExpression);
  updateDisplay();
  lastKeyType = "number";
}

function handleOperator(operator) {
  const ops = {
    divide: "÷",
    multiply: "×",
    subtract: "−",
    add: "+",
  };
  const symbol = ops[operator];

  if (/[+−×÷]$/.test(currentExpression)) {
    currentExpression = currentExpression.slice(0, -1) + symbol;
  } else if (currentExpression) {
    currentExpression += symbol;
  }

  lastKeyType = "operator";
  updateDisplay();
}

function clearAll() {
  currentExpression = "";
  currentResult = "0";
  lastKeyType = "number";
  updateDisplay();
}

function toggleSign() {
  const parts = currentExpression.split(/([+−×÷])/);
  const last = parts.pop();
  if (!last) return;

  if (last.startsWith("-")) {
    parts.push(last.slice(1));
  } else {
    parts.push(`-${last}`);
  }

  currentExpression = parts.join("");
  currentResult = computeExpression(currentExpression);
  updateDisplay();
}

function applyPercent() {
  const parts = currentExpression.split(/([+−×÷])/);
  const last = parts.pop();
  if (!last) return;

  const value = parseFloat(last.replace(",", "."));
  if (Number.isNaN(value)) return;

  parts.push((value / 100).toString());
  currentExpression = parts.join("");
  currentResult = computeExpression(currentExpression);
  updateDisplay();
}

function handleEquals() {
  currentResult = computeExpression(currentExpression);
  currentExpression = currentResult;
  updateDisplay();
}

keys.forEach((key) => {
  key.addEventListener("click", () => {
    const value = key.dataset.value;
    const action = key.dataset.action;

    if (value !== undefined) {
      appendValue(value);
      return;
    }

    switch (action) {
      case "clear":
        clearAll();
        break;
      case "sign":
        toggleSign();
        break;
      case "percent":
        applyPercent();
        break;
      case "divide":
      case "multiply":
      case "subtract":
      case "add":
        handleOperator(action);
        break;
      case "equals":
        handleEquals();
        break;
      default:
        break;
    }
  });
});

document.addEventListener("keydown", (event) => {
  if (/^[0-9.]$/.test(event.key)) {
    appendValue(event.key);
  } else if (["+", "-", "*", "/"].includes(event.key)) {
    const map = {
      "+": "add",
      "-": "subtract",
      "*": "multiply",
      "/": "divide",
    };
    handleOperator(map[event.key]);
  } else if (event.key === "Enter" || event.key === "=") {
    handleEquals();
  } else if (event.key === "Escape") {
    clearAll();
  }
});

glowToggle.addEventListener("click", () => {
  const isActive = glowToggle.getAttribute("aria-pressed") === "true";
  glowToggle.setAttribute("aria-pressed", String(!isActive));
  document.body.classList.toggle("no-glow", isActive);
});

updateDisplay();
