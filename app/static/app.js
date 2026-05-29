const form = document.getElementById("calculator-form");
const leftValue = document.getElementById("left-value");
const operator = document.getElementById("operator");
const rightValue = document.getElementById("right-value");
const resultValue = document.getElementById("result-value");
const resultDetail = document.getElementById("result-detail");
const historyList = document.getElementById("history-list");
const refreshHistoryButton = document.getElementById("refresh-history");

function formatNumber(value) {
  if (Number.isInteger(value)) {
    return value.toString();
  }
  return Number.parseFloat(value.toFixed(6)).toString();
}

function renderHistory(items) {
  if (!items.length) {
    historyList.innerHTML = '<p class="empty-state">No calculations saved yet.</p>';
    return;
  }

  historyList.innerHTML = items
    .map(
      (item) => `
        <article class="history-item">
          <div>
            <strong>${formatNumber(item.left_value)} ${item.operator} ${formatNumber(item.right_value)} = ${formatNumber(item.result_value)}</strong>
            <p>${new Date(item.created_at).toLocaleString()}</p>
          </div>
        </article>
      `,
    )
    .join("");
}

async function loadHistory() {
  const response = await fetch("/api/history?limit=20");
  const items = await response.json();
  renderHistory(items);
}

async function calculate(event) {
  event.preventDefault();

  const payload = {
    left: Number.parseFloat(leftValue.value),
    operator: operator.value,
    right: Number.parseFloat(rightValue.value),
  };

  resultDetail.textContent = "Calculating and saving to Postgres...";

  const response = await fetch("/api/calculate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    resultValue.textContent = "Error";
    resultDetail.textContent = data.detail ?? "Calculation failed";
    return;
  }

  resultValue.textContent = formatNumber(data.result);
  resultDetail.textContent = `${formatNumber(data.left)} ${data.operator} ${formatNumber(data.right)} was stored successfully.`;
  await loadHistory();
}

form.addEventListener("submit", calculate);
refreshHistoryButton.addEventListener("click", loadHistory);

loadHistory().catch(() => {
  historyList.innerHTML = '<p class="empty-state">Database is not ready yet.</p>';
});
