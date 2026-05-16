import { api } from "../services/api.js";
import { fmt, currentYearMonth } from "../utils/formatters.js";
import { txBadge, txAmount } from "../utils/badges.js";

export class DashboardPage {
  constructor(chartsManager) {
    this.charts = chartsManager;
  }

  async render() {
    const currentMonth = new Date().toISOString().slice(0, 7);
  
    const [summary, accounts] = await Promise.all([
      api.dashboard.summary(currentMonth),
      api.accounts.list(),
    ]);
  
    this._renderStats(summary, accounts);
    await this._renderRecent();
    this._renderCatBars(summary.expenses_by_category);
    await this.charts.renderDashboard();
  }

  _renderStats({ transactions_summary: s, accounts }) {
    const inc = s?.income?.total ?? 0;
    const exp = (s?.expense?.total ?? 0) + (s?.expense_tc?.total ?? 0);
    const invested = accounts.filter(a => a.type === "investment")
      .reduce((sum, a) => sum + a.current_balance, 0);
    const net = accounts.filter(a => a.type !== "credit")
      .reduce((sum, a) => sum + a.current_balance, 0);

    document.getElementById("dash-stats").innerHTML = `
      <div class="card card-sm"><div class="stat-label">Ingresos del mes</div><div class="stat-val green">${fmt(inc)}</div><div class="stat-meta">${s?.income?.count ?? 0} transacciones</div></div>
      <div class="card card-sm"><div class="stat-label">Egresos del mes</div><div class="stat-val red">${fmt(exp)}</div></div>
      <div class="card card-sm"><div class="stat-label">Invertido total</div><div class="stat-val accent">${fmt(invested)}</div></div>
      <div class="card card-sm"><div class="stat-label">Balance neto</div><div class="stat-val ${net >= 0 ? "green" : "red"}">${fmt(net)}</div></div>`;
  }

  async _renderRecent() {
    const result = await api.transactions.list({ page_size: 8, page: 1 });
    const tbody = document.getElementById("dash-recent");
    if (!tbody) return;
  
    tbody.innerHTML = result.items?.length
      ? `<thead><tr><th>Fecha</th><th>Descripción</th><th>Tipo</th><th style="text-align:right">Valor</th></tr></thead>` +
        result.items.map(t => `<tr>
          <td style="color:var(--text3)">${t.date}</td>
          <td>${t.description}</td>
          <td>${txBadge(t.type)}</td>
          <td style="text-align:right">${txAmount(t.type, t.amount, fmt)}</td>
        </tr>`).join("")
      : `<tr><td colspan="4" style="text-align:center;color:var(--text3);padding:24px">Sin transacciones</td></tr>`;
  
    document.getElementById("btn-ver-todas")?.addEventListener("click", () => {
      window.app.sidebar.navigate("transactions");
    });
  }

  _renderCatBars(cats = []) {
    const el = document.getElementById("dash-cat-bars");
    if (!el) return;
    const max = cats[0]?.total || 1;
    el.innerHTML = cats.slice(0, 10).map(c => `
      <div class="progress-row">
        <div class="progress-header"><span>${c.emoji} ${c.name}</span><span style="color:var(--text3)">${fmt(c.total)}</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${Math.round(c.total/max*100)}%;background:${c.color}"></div></div>
      </div>`).join("") || `<div style="color:var(--text3);font-size:13px;padding:20px 0">Sin gastos este mes</div>`;
  }
}
