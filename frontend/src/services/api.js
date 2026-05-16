/**
 * Capa de comunicación con el backend.
 * ÚNICO lugar donde se hacen fetch() calls.
 * Cambiar BASE_URL aquí si el backend cambia de host/puerto.
 */

const BASE_URL = window.location.hostname === "localhost"
  ? "http://localhost:8000/api/v1"
  : "https://finanzas-personales-uzs9.onrender.com/api/v1";

async function request(method, path, body = null) {
  const token = sessionStorage.getItem("auth_token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${path}`, opts);

  if (res.status === 401) {
    // Token expirado o inválido — redirigir al login
    sessionStorage.removeItem("auth_token");
    sessionStorage.removeItem("auth_user");
    window.location.href = "/login.html";
    return;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Error ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

// ── Accounts ────────────────────────────────────────────────────
export const api = {
  accounts: {
    list:   ()           => request("GET",    "/accounts/"),
    get:    (id)         => request("GET",    `/accounts/${id}`),
    create: (data)       => request("POST",   "/accounts/", data),
    update: (id, data)   => request("PATCH",  `/accounts/${id}`, data),
    delete: (id)         => request("DELETE", `/accounts/${id}`),
  },

  // ── Categories ────────────────────────────────────────────────
  categories: {
    list:   ()           => request("GET",    "/categories/"),
    create: (data)       => request("POST",   "/categories/", data),
    update: (id, data)   => request("PATCH",  `/categories/${id}`, data),
    delete: (id)         => request("DELETE", `/categories/${id}`),
  },

  // ── Transactions ──────────────────────────────────────────────
  transactions: {
    list:   (params = {}) => {
      const qs = new URLSearchParams(
        Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
      ).toString();
      return request("GET", `/transactions/${qs ? "?" + qs : ""}`);
    },
    create: (data)       => request("POST",   "/transactions/", data),
    update: (id, data)   => request("PATCH",  `/transactions/${id}/`, data),
	get:    (id)          => request("GET", `/transactions/${id}/`),
    delete: (id)         => request("DELETE", `/transactions/${id}/`),
    dateRange:          () => request("GET", "/transactions/date-range/"),
  },

  // ── Dashboard ─────────────────────────────────────────────────
  dashboard: {
    summary: (month)     => request("GET", `/dashboard/summary/?month=${month}`),
    monthly: (months=6)  => request("GET", `/dashboard/charts/monthly/?months=${months}`),
    expenses: (dateFrom, dateTo) => request("GET", `/dashboard/expenses-by-category/?date_from=${dateFrom}&date_to=${dateTo}`),
  },

  // ── Health ────────────────────────────────────────────────────
  health: () => fetch("http://localhost:8000/api/health").then(r => r.json()),

  // ── Auth ────────────────────────────────────────────────────
  auth: {
  login:          (data)  => request("POST", "/auth/login/", data),
  register:       (data)  => request("POST", "/auth/register/", data),
  changePassword: (data)  => request("POST", "/auth/change-password/", data),
  forgotPassword: (data)  => request("POST", "/auth/forgot-password/", data),
  resetPassword:  (data)  => request("POST", "/auth/reset-password/", data),
},
};
