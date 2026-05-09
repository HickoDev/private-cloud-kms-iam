import { apiDelete, apiGet, apiPost } from "./api.js";

export function listKeys() {
  return apiGet("/api/keys");
}

export function createKey(payload) {
  return apiPost("/api/keys", payload);
}

export function disableKey(keyId) {
  return apiPost(`/api/keys/${keyId}/disable`);
}

export function rotateKey(keyId) {
  return apiPost(`/api/keys/${keyId}/rotate`);
}

export function listKeyVersions(keyId) {
  return apiGet(`/api/keys/${keyId}/versions`);
}

export function encryptData(keyId, plaintext) {
  return apiPost(`/api/keys/${keyId}/encrypt`, { plaintext });
}

export function decryptData(keyId, payload) {
  return apiPost(`/api/keys/${keyId}/decrypt`, payload);
}

export function listKeyAccess(keyId) {
  return apiGet(`/api/keys/${keyId}/access`);
}

export function grantKeyAccess(keyId, payload) {
  return apiPost(`/api/keys/${keyId}/access`, payload);
}

export function revokeKeyAccess(keyId, userId) {
  return apiDelete(`/api/keys/${keyId}/access/${userId}`);
}
