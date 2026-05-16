import { api } from "../services/api.js";
import { toast } from "../components/toast.js";
import { modal } from "../components/modal.js";
import { ColorPicker } from "../components/colorPicker.js";

export class CategoriesPage {
  constructor() {
    this.picker = new ColorPicker("cat-colors", "#22d48f");
    this._bindForm();
  }

  async render() {
    const cats = await api.categories.list();
    document.getElementById("cat-grid").innerHTML = cats.map(c => `
      <div class="card card-sm" style="border-left:3px solid ${c.color}">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <span style="font-size:22px">${c.emoji}</span>
          <div style="display:flex;gap:6px">
            <button class="btn-mini" data-edit="${c.id}">✏️</button>
            <button class="btn-mini danger" data-delete="${c.id}">✕</button>
          </div>
        </div>
        <div style="font-weight:500;font-size:14px;margin-bottom:4px">${c.name}</div>
        <div style="font-size:12px;color:var(--text3)">${c.transaction_count} transacciones</div>
      </div>`).join("") + `<div class="account-card new-card btn-open-cat"><span style="font-size:24px">+</span><span>Nueva categoría</span></div>`;

    document.getElementById("cat-grid").querySelectorAll("[data-edit]").forEach(btn =>
      btn.addEventListener("click", () => this.openEdit(btn.dataset.edit, cats)));
    document.getElementById("cat-grid").querySelectorAll("[data-delete]").forEach(btn =>
      btn.addEventListener("click", () => this.delete(btn.dataset.delete)));
    document.querySelectorAll(".btn-open-cat").forEach(btn =>
      btn.addEventListener("click", () => this.openNew())
);
  }

  openNew() {
    document.getElementById("cat-name").value = "";
    document.getElementById("cat-emoji").value = "";
    document.getElementById("cat-edit-id").value = "";
    this.picker.reset("#22d48f");
    modal.open("modal-cat");
  }

  openEdit(id, cats) {
    const c = cats.find(x => x.id === id);
    if (!c) return;
    document.getElementById("cat-name").value = c.name;
    document.getElementById("cat-emoji").value = c.emoji;
    document.getElementById("cat-edit-id").value = c.id;
    this.picker.reset(c.color);
    modal.open("modal-cat");
  }

  async delete(id) {
    try {
      await api.categories.delete(id);
      toast.show("Categoría eliminada", "success");
      this.render();
    } catch (e) { toast.show(e.message, "error"); }
  }

  _bindForm() {
    document.getElementById("btn-save-cat")?.addEventListener("click", () => this.save());
  }

  async save() {
    const id = document.getElementById("cat-edit-id").value;
    const data = {
      name:  document.getElementById("cat-name").value.trim(),
      emoji: document.getElementById("cat-emoji").value || "📦",
      color: this.picker.value,
    };
    if (!data.name) return toast.show("Ingresa un nombre", "error");
    try {
      id ? await api.categories.update(id, data) : await api.categories.create(data);
      modal.close("modal-cat");
      toast.show("Categoría guardada", "success");
      this.render();
    } catch (e) { toast.show(e.message, "error"); }
  }
}
