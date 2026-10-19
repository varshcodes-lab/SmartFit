const configuredUrl = import.meta.env.VITE_API_URL;

export const API_BASE_URL = (
  configuredUrl || "https://smartfit-70dv.onrender.com"
).replace(/\/+$/, "");