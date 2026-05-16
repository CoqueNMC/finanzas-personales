/**
 * Genera HTML de badges y amounts para transacciones.
 */

const TYPE_LABELS = {
  income:     ["income",   "Ingreso"],
  expense:    ["expense",  "Gasto"],
  expense_tc: ["expense",  "Gasto TC"],
  transfer:   ["transfer", "Pago TC"],
  invest:     ["invest",   "Inversión"],
  withdraw:   ["invest",   "Retiro inv."],
};

export const txBadge = (type) => {
  const [cls, label] = TYPE_LABELS[type] ?? ["", type];
  return `<span class="badge ${cls}">${label}</span>`;
};

export const txAmount = (type, amount, fmt) => {
  if (type === "income")   return `<span class="amount-pos">+${fmt(amount)}</span>`;
  if (type === "expense" || type === "expense_tc")
                           return `<span class="amount-neg">-${fmt(amount)}</span>`;
  return `<span class="amount-neu">${fmt(amount)}</span>`;
};
