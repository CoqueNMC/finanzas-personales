/**
 * app.js — Orquestador principal.
 * Inicializa páginas y maneja la navegación.
 */

// Verificar autenticación
const token = sessionStorage.getItem("auth_token");
if (!token) {
  window.location.href = "/login.html";
}
import { Sidebar }          from "./components/sidebar.js";
import { ChartsManager }    from "./pages/charts.js";
import { DashboardPage }    from "./pages/dashboard.js";
import { AccountsPage }     from "./pages/accounts.js";
import { TransactionsPage } from "./pages/transactions.js";
import { CategoriesPage }   from "./pages/categories.js";

const PAGE_CONFIG = {
  dashboard:    { title: "Dashboard",      sub: "Resumen financiero",  action: "Transacción" },
  accounts:     { title: "Cuentas",        sub: "Gestiona tus cuentas", action: "Nueva cuenta" },
  transactions: { title: "Transacciones",  sub: "Historial completo",  action: "Transacción" },
  charts:       { title: "Gráficas",       sub: "Análisis visual",     action: null },
  categories:   { title: "Categorías",     sub: "Organiza tus gastos", action: null },
  profile: { title: "Perfil", sub: "Configuración de cuenta", action: null },
};

class App {
  constructor() {
    this.charts = new ChartsManager();
    this.dashboard = new DashboardPage(this.charts);
    this.accounts  = new AccountsPage();
    this.transactions = new TransactionsPage((count) => this.sidebar?.updateTxCount(count));
    this.categories = new CategoriesPage();
	this.dashboard = new DashboardPage(this.charts, this);

    this.sidebar = new Sidebar((page) => this._onNavigate(page));
    this._currentPage = "dashboard";

    // Bind topbar action button
    document.getElementById("topbar-action")?.addEventListener("click", () => this._topbarAction());

    // Chart months selector
    document.getElementById("chart-months")?.addEventListener("change", () => this.charts.renderDashboard());
  }

  async init() {
    await this._onNavigate("dashboard");
  }

  async _onNavigate(page) {
    this._currentPage = page;
    // Hide all screens, show target
    document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
    document.getElementById(`screen-${page}`)?.classList.add("active");

    // Update topbar
    const cfg = PAGE_CONFIG[page];
    if (cfg) {
      document.getElementById("page-title").textContent = cfg.title;
      document.getElementById("page-sub").textContent = cfg.sub;
      const btn = document.getElementById("topbar-action");
      if (btn) {
        btn.textContent = `+ ${cfg.action}`;
        btn.style.display = cfg.action ? "" : "none";
      }

    if (page === "profile") {
      document.getElementById("btn-change-password").onclick = async () => {
        const current = document.getElementById("cp-current").value;
        const newPass = document.getElementById("cp-new").value;
        const confirm = document.getElementById("cp-confirm").value;
        if (!current || !newPass || !confirm) return toast.show("Completa todos los campos", "error");
        if (newPass !== confirm) return toast.show("Las contraseñas no coinciden", "error");
        if (newPass.length < 6) return toast.show("Mínimo 6 caracteres", "error");
        try {
          await api.auth.changePassword({ current_password: current, new_password: newPass });
          toast.show("Contraseña actualizada", "success");
          document.getElementById("cp-current").value = "";
          document.getElementById("cp-new").value = "";
          document.getElementById("cp-confirm").value = "";
        } catch(e) { toast.show(e.message, "error"); }
      };
    }
    }

    // Render page
    try {
      if (page === "dashboard") await this.dashboard.render();
      if (page === "accounts")  await this.accounts.render();
      if (page === "transactions") {
        await this.transactions.populateSelects();
        await this.transactions.render();
      }
      if (page === "charts")     await this.charts.renderFullCharts();
      if (page === "categories") await this.categories.render();
    } catch (e) {
      console.error(`Error rendering ${page}:`, e);
    }
  }

  _topbarAction() {
    if (this._currentPage === "accounts")     this.accounts.openNew();
    if (this._currentPage === "transactions") this.transactions.openNew();
    if (this._currentPage === "categories")   this.categories.openNew();
    if (this._currentPage === "dashboard")    this.transactions.openNew();
  }
}

// Boot
const app = new App();
app.init();

// Cargar datos del usuario en sidebar
const authUser = JSON.parse(sessionStorage.getItem("auth_user") || "{}");
if (authUser.name) {
  document.getElementById("user-name").textContent = authUser.name;
  document.getElementById("user-email").textContent = authUser.email;
}

// Logout
window.doLogout = () => {
  sessionStorage.removeItem("auth_token");
  sessionStorage.removeItem("auth_user");
  window.location.href = "/login.html";
};

// Exponer globalmente para acceso desde componentes
window.app = app;