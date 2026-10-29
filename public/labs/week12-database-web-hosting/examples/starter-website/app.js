"use strict";
const labels = {w:"White", b:"Black", a:"Asian", h:"Hispanic", o:"Other"};
async function loadChart() {
  try {
    const response = await fetch("assets/category_counts.json");
    if (!response.ok) throw new Error(`Data request failed: HTTP ${response.status}`);
    const rows = await response.json();
    if (!Array.isArray(rows) || !rows.length || rows.some(row =>
      !Object.hasOwn(labels, row.category) || !Number.isFinite(row.sample_dots) || row.sample_dots < 0)) {
      throw new Error("The query export does not match the expected category/count format.");
    }
    rows.sort((a,b) => b.sample_dots-a.sample_dots);
    const total = rows.reduce((sum,row) => sum + row.sample_dots,0);
    const maximum = Math.max(...rows.map(row=>row.sample_dots),1);
    document.getElementById("total").textContent = `${total.toLocaleString()} sample dots in this Pennsylvania teaching extract.`;
    const chart = document.getElementById("chart");
    chart.replaceChildren();
    for (const row of rows) {
      const item = document.createElement("li");
      const label = document.createElement("div"); label.className = "bar-label";
      const name = document.createElement("span"); name.textContent = labels[row.category];
      const count = document.createElement("span"); count.className = "count"; count.textContent = row.sample_dots.toLocaleString();
      label.append(name,count);
      const track = document.createElement("div"); track.className = "track"; track.setAttribute("aria-hidden","true");
      const bar = document.createElement("div"); bar.className = "bar"; bar.style.width = `${100*row.sample_dots/maximum}%`;
      track.append(bar); item.append(label,track); chart.append(item);
    }
  } catch (error) {
    document.getElementById("total").textContent = "The chart data could not be loaded.";
    const message = document.getElementById("error"); message.hidden = false;
    message.textContent = `${error.message} Check assets/category_counts.json and preview through http://localhost:8000 rather than file://.`;
  }
}
loadChart();
