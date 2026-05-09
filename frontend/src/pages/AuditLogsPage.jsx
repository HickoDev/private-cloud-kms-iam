import { useEffect, useState } from "react";

import DataTable from "../components/DataTable.jsx";
import { listAuditLogs } from "../services/auditService.js";

const columns = [
  {
    key: "created_at",
    label: "Time",
    render: (row) => new Date(row.created_at).toLocaleString(),
  },
  { key: "action", label: "Action" },
  { key: "status", label: "Status" },
  { key: "user_id", label: "User" },
  { key: "details", label: "Details" },
];

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [filters, setFilters] = useState({
    action: "",
    status: "",
    user_id: "",
  });
  const [error, setError] = useState("");

  async function loadLogs(nextFilters = filters) {
    setError("");

    try {
      setLogs(await listAuditLogs(nextFilters));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadLogs();
  }, []);

  function updateFilter(field, value) {
    setFilters((current) => ({ ...current, [field]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    loadLogs();
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Traceability</p>
          <h1>Audit Logs</h1>
        </div>
      </header>

      {error ? <p className="error-message">{error}</p> : null}

      <form className="form-panel" onSubmit={handleSubmit}>
        <h2>Filters</h2>
        <div className="form-grid">
          <label>
            Action
            <input
              value={filters.action}
              onChange={(event) => updateFilter("action", event.target.value)}
              placeholder="KEY_CREATED"
            />
          </label>
          <label>
            Status
            <select
              value={filters.status}
              onChange={(event) => updateFilter("status", event.target.value)}
            >
              <option value="">Any</option>
              <option value="SUCCESS">SUCCESS</option>
              <option value="FAILED">FAILED</option>
            </select>
          </label>
          <label>
            User ID
            <input
              type="number"
              value={filters.user_id}
              onChange={(event) => updateFilter("user_id", event.target.value)}
            />
          </label>
        </div>
        <div className="button-row">
          <button type="submit">Apply filters</button>
          <button
            type="button"
            className="secondary-button compact-button"
            onClick={() => {
              const emptyFilters = { action: "", status: "", user_id: "" };
              setFilters(emptyFilters);
              loadLogs(emptyFilters);
            }}
          >
            Clear
          </button>
        </div>
      </form>

      <DataTable columns={columns} rows={logs} />
    </section>
  );
}
