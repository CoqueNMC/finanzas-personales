/**
 * Componente Sidebar: navegación y estado de API.
 */
import { api } from "../services/api.js";

export class Sidebar {
  constructor(onNavigate) {
    this.onNavigate = onNavigate;
    this._bindNav();
    this._checkHealth();
  }

  _bindNav() {
    document.querySelectorAll(".nav-item[data-page]").forEach((item) => {
      item.addEventListener("click", () => this.navigate(item.dataset.page));
    });
  }

  navigate(page) {
    document.querySelectorAll(".nav-item").forEach((el) => el.classList.remove("active"));
    document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add("active");
    this.onNavigate(page);
  }

  updateTxCount(count) {
    const badge = document.getElementById("tx-badge");
    if (badge) badge.textContent = count.toLocaleString();
  }

  async _checkHealth() {
    const dot = document.getElementById("api-dot");
    const label = document.getElementById("api-label");
  
    const check = async () => {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000); // 3s timeout
  
        const res = await fetch("http://localhost:8000/api/health", {
          signal: controller.signal
        });
        clearTimeout(timeout);
  
        const h = await res.json();
        if (dot) dot.className = "status-dot " + (h.status === "ok" ? "ok" : "err");
        if (label) label.textContent = h.status === "ok" ? "API conectada" : "Error de BD";
      } catch (e) {
        if (dot) dot.className = "status-dot err";
        if (label) label.textContent = "Sin conexión";
  
        // Reintentar cada 5 segundos si falla
        setTimeout(check, 5000);
      }
    };
  
    await check();
  }

}
