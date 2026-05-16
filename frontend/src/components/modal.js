/**
 * Componente Modal genérico.
 * Uso: modal.open("modal-id") / modal.close("modal-id")
 */
export const modal = {
  open(id)  { document.getElementById(id)?.classList.add("open"); },
  close(id) { document.getElementById(id)?.classList.remove("open"); },
};

// Cerrar al click fuera del modal
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("overlay")) {
    e.target.classList.remove("open");
  }
});
