import { api } from "../services/api.js";
import { fmt } from "../utils/formatters.js";
import { toast } from "../components/toast.js";
import { modal } from "../components/modal.js";
import { ColorPicker } from "../components/colorPicker.js";

const TYPE_LABELS = { cash:"Efectivo", credit:"Tarjeta de crédito", investment:"Inversión", savings:"Ahorros", other:"Otro" };

export class AccountsPage {
  constructor() {
    this.picker = new ColorPicker("acc-colors", "#7c6aff");
    this._bindForm();
  }

  async render() {
    const accounts = await api.accounts.list();
    this._renderGrid(accounts);
  }

  _renderGrid(accounts) {
    const grid = document.getElementById("accounts-grid");
    grid.innerHTML = accounts.map(a => {
      const isCredit = a.type === "credit";
      const bal = a.current_balance;
      const cls = isCredit ? (bal <= 0 ? "positive" : "negative") : (bal >= 0 ? "positive" : "negative");
      const disp = isCredit ? (bal <= 0 ? fmt(Math.abs(bal)) : `-${fmt(bal)}`) : fmt(bal);
      return `<div class="account-card" style="border-top:3px solid ${a.color}">
        <span class="account-emoji">${a.emoji}</span>
        <div class="account-name">${a.name}</div>
        <div class="account-type">${TYPE_LABELS[a.type] ?? a.type}</div>
        <div class="account-balance ${cls}">${disp}</div>
        <div class="account-actions">
          <button class="btn-mini" data-edit="${a.id}">✏️ Editar</button>
          <button class="btn-mini danger" data-delete="${a.id}">Eliminar</button>
        </div>
      </div>`;
    }).join("") + `<div class="account-card new-card" id="btn-new-account"><span style="font-size:24px">+</span><span>Nueva cuenta</span></div>`;

    grid.querySelectorAll("[data-edit]").forEach(btn =>
      btn.addEventListener("click", () => this.openEdit(btn.dataset.edit)));
    grid.querySelectorAll("[data-delete]").forEach(btn =>
      btn.addEventListener("click", () => this.delete(btn.dataset.delete)));
    document.getElementById("btn-new-account")?.addEventListener("click", () => this.openNew());
  }

  openNew() {
    document.getElementById("acc-edit-id").value = "";
    document.getElementById("acc-name").value = "";
    document.getElementById("acc-emoji").value = "";
    document.getElementById("acc-balance").value = "";
    document.getElementById("modal-acc-title").textContent = "Nueva cuenta";
    this.picker.reset("#7c6aff");
    modal.open("modal-account");
  }

  async openEdit(id) {
    const a = await api.accounts.get(id);
    document.getElementById("acc-edit-id").value = a.id;
    document.getElementById("acc-name").value = a.name;
    document.getElementById("acc-type").value = a.type;
    document.getElementById("acc-emoji").value = a.emoji;
    document.getElementById("acc-balance").value = a.initial_balance;
    document.getElementById("modal-acc-title").textContent = "Editar cuenta";
    this.picker.reset(a.color);
    modal.open("modal-account");
  }

  async delete(id) {
    if (!confirm("¿Eliminar esta cuenta?")) return;
    try {
      await api.accounts.delete(id);
      toast.show("Cuenta eliminada", "success");
      this.render();
    } catch (e) { toast.show(e.message, "error"); }
  }

  _bindForm() {
    document.getElementById("btn-save-account")?.addEventListener("click", () => this.save());
  }

  async save() {
    const id = document.getElementById("acc-edit-id").value;
    const data = {
      name: document.getElementById("acc-name").value.trim(),
      type: document.getElementById("acc-type").value,
      emoji: document.getElementById("acc-emoji").value || "💰",
      color: this.picker.value,
      initial_balance: parseFloat(document.getElementById("acc-balance").value) || 0,
    };
    if (!data.name) return toast.show("Ingresa un nombre", "error");
    try {
      id ? await api.accounts.update(id, data) : await api.accounts.create(data);
      modal.close("modal-account");
      toast.show(id ? "Cuenta actualizada" : "Cuenta creada", "success");
      this.render();
    } catch (e) { toast.show(e.message, "error"); }
  }
}
