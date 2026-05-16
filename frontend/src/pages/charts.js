import { api } from "../services/api.js";
import { fmt, monthsBack, currentYearMonth } from "../utils/formatters.js";

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: "rgba(255,255,255,0.5)", font: { family: "DM Sans", size: 11 } } },
    tooltip: { callbacks: { label: (c) => " " + fmt(c.raw) } },
  },
  scales: {
    x: { ticks: { color: "rgba(255,255,255,0.35)", font: { family: "DM Sans", size: 11 } }, grid: { color: "rgba(255,255,255,0.04)" } },
    y: { ticks: { color: "rgba(255,255,255,0.35)", font: { family: "DM Sans", size: 10 }, callback: (v) => fmt(v) }, grid: { color: "rgba(255,255,255,0.04)" } },
  },
};
const PIE_DEFAULTS = {
  responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { position: "right", labels: { color: "rgba(255,255,255,0.5)", font: { family: "DM Sans", size: 11 }, boxWidth: 12 } },
    tooltip: { callbacks: { label: (c) => " " + fmt(c.raw) } },
  },
};

export class ChartsManager {
  constructor() { this._instances = {}; }

  _destroy(id) { this._instances[id]?.destroy(); delete this._instances[id]; }

  _make(id, config) {
    this._destroy(id);
    const canvas = document.getElementById(id);
    if (!canvas) return;
    this._instances[id] = new Chart(canvas, config);
  }

  async renderDashboard() {
    const months = parseInt(document.getElementById("chart-months")?.value ?? 1);
    const data = await api.dashboard.monthly(months);
    const labels = data.map(d => d.month);
  
    this._make("chart-incexp", { type: "bar", data: { labels, datasets: [
      { label: "Ingresos", data: data.map(d => d.income), backgroundColor: "rgba(34,212,143,0.7)", borderRadius: 4 },
      { label: "Egresos",  data: data.map(d => d.expense), backgroundColor: "rgba(255,94,122,0.7)", borderRadius: 4 },
    ]}, options: CHART_DEFAULTS });
  
    const fromDate = new Date();
    fromDate.setMonth(fromDate.getMonth() - months);
    const dateFrom = fromDate.toISOString().split("T")[0];
    const dateTo = new Date().toISOString().split("T")[0];
  
    const cats = await api.dashboard.expenses(dateFrom, dateTo);
  
    this._make("chart-cats", { type: "doughnut", data: {
      labels: cats.slice(0, 7).map(c => c.name),
      datasets: [{ 
        data: cats.slice(0, 7).map(c => c.total), 
        backgroundColor: cats.slice(0, 7).map(c => c.color + "cc"), 
        borderWidth: 0 
      }],
    }, options: PIE_DEFAULTS });
  }

  async renderFullCharts() {
    const data = await api.dashboard.monthly(12);
    const labels = data.map(d => d.month);
    const balances = data.map(d => d.income - d.expense);

    this._make("chart-monthly", { type: "line", data: { labels, datasets: [
      { label: "Ingresos", data: data.map(d => d.income), borderColor: "#22d48f", backgroundColor: "rgba(34,212,143,0.08)", tension: .4, fill: true },
      { label: "Egresos",  data: data.map(d => d.expense), borderColor: "#ff5e7a", backgroundColor: "rgba(255,94,122,0.08)", tension: .4, fill: true },
    ]}, options: CHART_DEFAULTS });

    this._make("chart-balance", { type: "bar", data: { labels, datasets: [
      { label: "Balance neto", data: balances, backgroundColor: balances.map(v => v >= 0 ? "rgba(34,212,143,0.7)" : "rgba(255,94,122,0.7)"), borderRadius: 4 },
    ]}, options: CHART_DEFAULTS });
  }
}
