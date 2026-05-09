import { apiGet, apiPost, apiPut } from "./api.js";

export function listUsers() {
  return apiGet("/api/users");
}

export function createUser(payload) {
  return apiPost("/api/users", payload);
}

export function updateUser(userId, payload) {
  return apiPut(`/api/users/${userId}`, payload);
}

export function assignRoles(userId, roles) {
  return apiPost(`/api/users/${userId}/roles`, { roles });
}

export function listRoles() {
  return apiGet("/api/roles");
}
