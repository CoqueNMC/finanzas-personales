/**
 * Componente Sidebar: navegación y estado de API.
 */
import { api } from "../services/api.js";

export class Sidebar {
  constructor(onNavigate) {
    this.onNavigate = onNavigate;
    this._bindNav();
    this._bindToggle();
    this._checkHealth();
  }

  _bindNav() {
    document.querySelectorAll(".sidebar [data-page]").forEach((item) => {
      item.addEventListener("click", () => this.navigate(item.dataset.page));
    });
  }

  navigate(page) {
    document.querySelectorAll(".nav-item").forEach((el) => el.classList.remove("active"));
    document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add("active");
    if (this._isMobile()) this.close();
    this.onNavigate(page);
  }

  // ── Mostrar / ocultar menú ──────────────────────────────
  _isMobile() { return window.matchMedia("(max-width: 768px)").matches; }

  _bindToggle() {
    document.getElementById("menu-toggle")?.addEventListener("click", () => this.toggle());
    document.getElementById("sidebar-backdrop")?.addEventListener("click", () => this.close());
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") this.close(); });
    // Escritorio: recordar si el usuario lo dejó colapsado
    try {
      if (localStorage.getItem("sidebar_collapsed") === "1") document.body.classList.add("sidebar-collapsed");
    } catch {}
  }

  toggle() {
    if (this._isMobile()) {
      document.body.classList.toggle("sidebar-open");
    } else {
      const collapsed = document.body.classList.toggle("sidebar-collapsed");
      try { localStorage.setItem("sidebar_collapsed", collapsed ? "1" : "0"); } catch {}
    }
    this._syncAria();
  }

  close() {
    document.body.classList.remove("sidebar-open");
    this._syncAria();
  }

  _syncAria() {
    const open = this._isMobile()
      ? document.body.classList.contains("sidebar-open")
      : !document.body.classList.contains("sidebar-collapsed");
    document.getElementById("menu-toggle")?.setAttribute("aria-expanded", String(open));
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
        const apiBase = window.location.hostname === "localhost"
          ? "http://localhost:8000"
          : "https://finanzas-personales-uzs9.onrender.com";
          const res = await fetch(`${apiBase}/api/health`, {
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
