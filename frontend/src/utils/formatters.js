/**
 * Helpers de formato. Importar donde se necesiten (DRY).
 */

export const fmt = (n) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency", currency: "COP",
    minimumFractionDigits: 0, maximumFractionDigits: 0,
  }).format(n ?? 0);

export const fmtDate = (d) =>
  new Date(d + "T00:00:00").toLocaleDateString("es-CO", {
    day: "2-digit", month: "short", year: "numeric",
  });

export const currentYearMonth = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
};

export const monthsBack = (n) => {
  const result = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date();
    d.setMonth(d.getMonth() - i);
    result.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`);
  }
  return result;
};
