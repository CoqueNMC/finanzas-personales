import { api } from "../services/api.js";
import { fmt } from "../utils/formatters.js";
import { txBadge, txAmount } from "../utils/badges.js";
import { toast } from "../components/toast.js";
import { modal } from "../components/modal.js";

export class TransactionsPage {
  constructor(onCountUpdate) {
    this.page = 1;
    this.onCountUpdate = onCountUpdate;
    this._bindFilters();
    this._bindForm();
  }

  async render() {
    const params = this._getFilters();
    const result = await api.transactions.list({ ...params, page: this.page });
    this._renderTable(result.items);
    this._renderPagination(result.total, result.pages);
    this.onCountUpdate?.(result.total);
  }

  async populateSelects() {
    const [accounts, categories] = await Promise.all([api.accounts.list(), api.categories.list()]);
    ["filter-account", "tx-cuenta", "tx-destino"].forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      const prev = sel.value;
      const prefix = id.startsWith("filter") ? '<option value="">Todas las cuentas</option>' : "";
      sel.innerHTML = prefix + accounts.map(a => `<option value="${a.id}">${a.emoji} ${a.name}</option>`).join("");
      sel.value = prev;
    });
    ["filter-cat", "tx-cat"].forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      const prev = sel.value;
      const prefix = id.startsWith("filter") ? '<option value="">Todas las categorías</option>' : "";
      sel.innerHTML = prefix + categories.map(c => `<option value="${c.id}">${c.emoji} ${c.name}</option>`).join("");
      sel.value = prev;
    });
  }

  _renderTable(items) {
    document.getElementById("tx-body").innerHTML = items.length
      ? items.map(t => `<tr>
          <td style="color:var(--text3);white-space:nowrap">${t.date}</td>
          <td>${t.description}</td>
          <td><span class="cat-pill"><span class="tag-dot" style="background:${t.category_color ?? "#555"}"></span>${t.category_emoji ?? "📦"} ${t.category_name ?? "Varios"}</span></td>
          <td style="color:var(--text2)">${t.account_emoji ?? "❓"} ${t.account_name ?? "—"}</td>
          <td>${txBadge(t.type)}</td>
          <td style="text-align:right;font-family:var(--font-display)">${txAmount(t.type, t.amount, fmt)}</td>
          <td style="display:flex;gap:6px;">
            <button class="btn-mini" data-edit="${t.id}">✏️</button>
            <button class="btn-mini danger" data-delete="${t.id}">✕</button>
        </td>
        </tr>`).join("")
      : `<tr><td colspan="7" style="text-align:center;color:var(--text3);padding:40px">Sin transacciones</td></tr>`;

    document.getElementById("tx-body").querySelectorAll("[data-delete]").forEach(btn =>
      btn.addEventListener("click", () => this.delete(btn.dataset.delete)));
	  
	document.getElementById("tx-body").querySelectorAll("[data-edit]").forEach(btn =>
	  btn.addEventListener("click", () => this.openEdit(btn.dataset.edit)));
  }


  _renderPagination(total, pages) {
    document.getElementById("tx-count-label").textContent =
      `${total.toLocaleString()} transacciones · Pág ${this.page} de ${pages}`;
  }

  _getFilters() {
    return {
      search:      document.getElementById("search-tx")?.value || undefined,
      type:        document.getElementById("filter-type")?.value || undefined,
      account_id:  document.getElementById("filter-account")?.value || undefined,
      category_id: document.getElementById("filter-cat")?.value || undefined,
      date_from:   document.getElementById("filter-date-from")?.value || undefined,
      date_to:     document.getElementById("filter-date-to")?.value || undefined,
    };
  }

  _bindFilters() {
    ["search-tx","filter-type","filter-account","filter-cat","filter-date-from","filter-date-to"].forEach(id => {
      document.getElementById(id)?.addEventListener("input", () => { this.page = 1; this.render(); });
      document.getElementById(id)?.addEventListener("change", () => { this.page = 1; this.render(); });
    });
    document.getElementById("btn-prev")?.addEventListener("click", () => { if (this.page > 1) { this.page--; this.render(); } });
    document.getElementById("btn-next")?.addEventListener("click", () => { this.page++; this.render(); });
    this._bindTipoChange();
  }

  _bindForm() {
    document.getElementById("tx-tipo")?.addEventListener("change", () => {
      const t = document.getElementById("tx-tipo").value;
      document.getElementById("tx-destino-group").style.display =
        ["transfer","invest","withdraw", "move"].includes(t) ? "" : "none";
    });
    document.getElementById("btn-save-tx")?.addEventListener("click", () => this.save());
  }

  async openNew() {
    this._editingId = null;
    this._restoreAccountSelects();
    document.getElementById("modal-tx-title").textContent = "Nueva transacción";
    await this.populateSelects();
    document.getElementById("tx-desc").value = "";
    document.getElementById("tx-valor").value = "";
    document.getElementById("tx-fecha").value = new Date().toISOString().split("T")[0];
    document.getElementById("tx-tipo").value = "expense";
    document.getElementById("tx-destino-group").style.display = "none";
    this._onTipoChange();
    modal.open("modal-tx");
  }
    
  async openEdit(id) {
    this._restoreAccountSelects();
    await this.populateSelects();
    const tx = await api.transactions.get(id);
    const accounts = await api.accounts.list();

    document.getElementById("modal-tx-title").textContent = "Editar transacción";
    document.getElementById("tx-desc").value = tx.description;
    document.getElementById("tx-valor").value = tx.amount;
    document.getElementById("tx-fecha").value = tx.date;
    document.getElementById("tx-tipo").value = tx.type;
    document.getElementById("tx-cat").value = tx.category_id ?? "";

    // Cuenta origen
    const accExists = accounts.find(a => a.id === tx.account_id);
    const cuentaGroup = document.getElementById("tx-cuenta").parentElement;
    if (!accExists && tx.account_id) {
      cuentaGroup.innerHTML = `
        <label class="form-label">Cuenta origen</label>
        <div style="padding:10px 12px;background:var(--bg4);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:14px;color:var(--text3);">
          ${tx.account_emoji ?? "❓"} ${tx.account_name ?? "Cuenta eliminada"}
          <span style="font-size:11px;color:var(--red);margin-left:8px;">(inactiva)</span>
        </div>
        <input type="hidden" id="tx-cuenta" value="${tx.account_id}">
      `;
    } else {
      document.getElementById("tx-cuenta").value = tx.account_id ?? "";
    }

    // Cuenta destino
    const needsDest = ["transfer", "invest", "withdraw", "move"].includes(tx-tipo);
    document.getElementById("tx-destino-group").style.display = needsDest ? "" : "none";

    if (needsDest && tx.to_account_id) {
      const toAccExists = accounts.find(a => a.id === tx.to_account_id);
      const destinoGroup = document.getElementById("tx-destino").parentElement;
      if (!toAccExists) {
        destinoGroup.innerHTML = `
          <label class="form-label">Cuenta destino</label>
          <div style="padding:10px 12px;background:var(--bg4);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:14px;color:var(--text3);">
            ❓ Cuenta destino eliminada
            <span style="font-size:11px;color:var(--red);margin-left:8px;">(inactiva)</span>
          </div>
          <input type="hidden" id="tx-destino" value="${tx.to_account_id}">
        `;
      } else {
        document.getElementById("tx-destino").value = tx.to_account_id ?? "";
      }
    }

    this._editingId = id;
    this._onTipoChange();
    modal.open("modal-tx");
  }

  async save() {
    const tipo = document.getElementById("tx-tipo").value;
    const cuentaSel = document.getElementById("tx-cuenta");
    const destinoSel = document.getElementById("tx-destino");
    cuentaSel.disabled = false;

    const data = {
      description: document.getElementById("tx-desc").value.trim(),
      amount:      parseFloat(document.getElementById("tx-valor").value),
      date:        document.getElementById("tx-fecha").value,
      type:        tipo,
      account_id:  cuentaSel.value || null,
      to_account_id: ["transfer", "invest", "withdraw"].includes(tipo)
        ? destinoSel.value : null,
      category_id: document.getElementById("tx-cat").value || null,
    };

    if (!data.description) return toast.show("Ingresa una descripción", "error");
    if (!data.amount || data.amount <= 0) return toast.show("Ingresa un valor válido", "error");

    // Rehabilitar selects antes de cerrar para no dejarlos bloqueados
    cuentaSel.disabled = false;
    destinoSel.disabled = false;

    try {
      if (this._editingId) {
        await api.transactions.update(this._editingId, data);
        this._editingId = null;
        toast.show("Transacción actualizada", "success");
      } else {
        await api.transactions.create(data);
        toast.show("Transacción guardada", "success");
      }
      modal.close("modal-tx");
      this.render();
    } catch (e) { toast.show(e.message, "error"); }
  }

  async delete(id) {
    try {
      await api.transactions.delete(id);
      toast.show("Eliminada", "success");
      this.render();
    } catch (e) { toast.show(e.message, "error"); }
  }

  _restoreAccountSelects() {
    const cuentaGroup = document.getElementById("tx-cuenta")?.parentElement;
    if (cuentaGroup && !cuentaGroup.querySelector("select#tx-cuenta")) {
      cuentaGroup.innerHTML = `
        <label class="form-label">Cuenta origen</label>
        <select class="form-select" id="tx-cuenta"></select>
      `;
    }
    const destinoGroup = document.getElementById("tx-destino")?.parentElement;
    if (destinoGroup && !destinoGroup.querySelector("select#tx-destino")) {
      destinoGroup.innerHTML = `
        <label class="form-label">Cuenta destino</label>
        <select class="form-select" id="tx-destino"></select>
      `;
    }
  }

  _bindTipoChange() {
    document.getElementById("tx-tipo")?.addEventListener("change", () => {
      this._onTipoChange();
    });
  }

  _onTipoChange() {
    const tipo = document.getElementById("tx-tipo").value;
    const needsDest = ["transfer", "invest", "withdraw", "move"].includes(tipo);
    const forceEfectivo = ["income", "expense"].includes(tipo);

    document.getElementById("tx-destino-group").style.display = needsDest ? "" : "none";

    const cuentaGroup = document.getElementById("tx-cuenta")?.parentElement;
    if (!cuentaGroup) return;

    if (forceEfectivo) {
      // Buscar cuenta efectivo
      const sel = document.getElementById("tx-cuenta");
      if (sel && sel.tagName === "SELECT") {
        const efectivoOpt = [...sel.options].find(o =>
          o.textContent.toLowerCase().includes("efectivo") ||
          o.textContent.includes("💵")
        );
        if (efectivoOpt) {
          sel.value = efectivoOpt.value;
          sel.disabled = true;
        }
      }
    } else {
      const sel = document.getElementById("tx-cuenta");
      if (sel && sel.tagName === "SELECT") {
        sel.disabled = false;
      }
    }
  }
}

