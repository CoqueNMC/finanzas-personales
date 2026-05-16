/**
 * Componente Toast: notificaciones no bloqueantes.
 * Uso: toast.show("Guardado", "success")
 */
const el = document.getElementById("toast");

export const toast = {
  show(msg, type = "success") {
    el.textContent = (type === "success" ? "✓ " : type === "error" ? "✕ " : "ℹ ") + msg;
    el.className = `toast ${type} show`;
    setTimeout(() => el.classList.remove("show"), 3200);
  },
};
