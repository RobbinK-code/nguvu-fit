const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5555";

function getToken() {
  return localStorage.getItem("nguvu_token");
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!res.ok) {
    const message =
      (data && (data.error || flattenErrors(data.errors))) || `Request failed (${res.status})`;
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

function flattenErrors(errors) {
  if (!errors) return null;
  if (Array.isArray(errors)) return errors.join(" ");
  if (typeof errors === "object") {
    return Object.entries(errors)
      .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(" ") : msgs}`)
      .join(" | ");
  }
  return String(errors);
}

export const api = {
  register: (payload) => request("/auth/register", { method: "POST", body: payload, auth: false }),
  login: (payload) => request("/auth/login", { method: "POST", body: payload, auth: false }),
  me: () => request("/auth/me"),

  getProfile: () => request("/profile"),
  updateProfile: (payload) => request("/profile", { method: "PATCH", body: payload }),

  getPlan: (days = 3) => request(`/plan?days=${days}`),

  getExercises: () => request("/exercises", { auth: false }),

  getLogs: () => request("/logs"),
  logWorkout: (payload) => request("/logs", { method: "POST", body: payload }),
  getStats: () => request("/logs/stats"),

  getQuoteOfDay: () => request("/quotes/today"),

  subscribe: (payload) => request("/payments/subscribe", { method: "POST", body: payload }),
  paymentStatus: (checkoutId) => request(`/payments/status/${checkoutId}`),

  adminListUsers: () => request("/admin/users"),
  adminStats: () => request("/admin/stats"),
  adminToggleAdmin: (id) => request(`/admin/users/${id}/toggle-admin`, { method: "PATCH" }),
  adminSetSubscription: (id, action, days) =>
    request(`/admin/users/${id}/subscription`, { method: "PATCH", body: { action, days } }),
  adminDeleteUser: (id) => request(`/admin/users/${id}`, { method: "DELETE" }),
};

export function setToken(token) {
  localStorage.setItem("nguvu_token", token);
}

export function clearToken() {
  localStorage.removeItem("nguvu_token");
}

export function hasToken() {
  return Boolean(getToken());
}
