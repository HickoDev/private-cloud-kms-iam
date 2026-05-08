import {
  apiGet,
  apiRequest,
  clearStoredToken,
  setStoredToken,
} from "./api.js";

export async function login(email, password) {
  const data = await apiRequest("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  setStoredToken(data.access_token);
  return data.user;
}

export function getCurrentUser() {
  return apiGet("/api/auth/me");
}

export function logout() {
  clearStoredToken();
}
