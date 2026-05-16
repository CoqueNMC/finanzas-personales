/**
 * Color picker reutilizable.
 * Uso: const picker = new ColorPicker("#acc-colors", "#7c6aff");
 *      picker.value => color seleccionado
 */
export class ColorPicker {
  constructor(containerId, defaultColor) {
    this.container = document.getElementById(containerId);
    this._value = defaultColor;
    this._init();
  }

  get value() { return this._value; }

  set value(color) {
    this._value = color;
    this.container?.querySelectorAll(".color-opt").forEach((opt) => {
      opt.classList.toggle("selected", opt.dataset.color === color);
    });
  }

  _init() {
    this.container?.addEventListener("click", (e) => {
      const opt = e.target.closest(".color-opt");
      if (!opt) return;
      this.value = opt.dataset.color;
    });
  }

  reset(color) { this.value = color; }
}
