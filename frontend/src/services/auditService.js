import { apiGet } from "./api.js";

export function listAuditLogs(filters = {}) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, value);
    }
  });

  const query = params.toString();
  return apiGet(`/api/audit-logs${query ? `?${query}` : ""}`);
}
