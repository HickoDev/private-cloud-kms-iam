import { useEffect, useMemo, useState } from "react";

import DataTable from "../components/DataTable.jsx";
import {
  createKey,
  disableKey,
  listKeyVersions,
  listKeys,
  rotateKey,
} from "../services/keyService.js";

function canManageKeys(user) {
  return user?.permissions?.includes("KEY_CREATE");
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "-";
}

export default function KeysPage({ user }) {
  const [keys, setKeys] = useState([]);
  const [versions, setVersions] = useState([]);
  const [selectedKey, setSelectedKey] = useState(null);
  const [form, setForm] = useState({
    name: "",
    description: "",
    algorithm: "AES-256-GCM",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const canManage = canManageKeys(user);

  const columns = useMemo(
    () => [
      { key: "name", label: "Name" },
      { key: "algorithm", label: "Algorithm" },
      { key: "status", label: "Status" },
      { key: "active_version", label: "Active Version" },
      {
        key: "created_at",
        label: "Created",
        render: (row) => formatDate(row.created_at),
      },
      {
        key: "actions",
        label: "Actions",
        render: (row) => (
          <div className="table-actions">
            <button type="button" onClick={() => loadVersions(row)}>
              Versions
            </button>
            {canManage ? (
              <>
                <button
                  type="button"
                  className="secondary-button compact-button"
                  disabled={row.status !== "ACTIVE"}
                  onClick={() => handleRotate(row)}
                >
                  Rotate
                </button>
                <button
                  type="button"
                  className="danger-button compact-button"
                  disabled={row.status !== "ACTIVE"}
                  onClick={() => handleDisable(row)}
                >
                  Disable
                </button>
              </>
            ) : null}
          </div>
        ),
      },
    ],
    [canManage],
  );

  async function loadKeys() {
    setError("");
    setIsLoading(true);

    try {
      setKeys(await listKeys());
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadKeys();
  }, []);

  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleCreateKey(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      await createKey(form);
      setForm({ name: "", description: "", algorithm: "AES-256-GCM" });
      setMessage("Key created.");
      await loadKeys();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRotate(key) {
    setError("");
    setMessage("");

    try {
      await rotateKey(key.id);
      setMessage(`Key ${key.name} rotated.`);
      await loadKeys();
      if (selectedKey?.id === key.id) {
        await loadVersions(key);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDisable(key) {
    setError("");
    setMessage("");

    try {
      await disableKey(key.id);
      setMessage(`Key ${key.name} disabled.`);
      await loadKeys();
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadVersions(key) {
    setError("");
    setSelectedKey(key);

    try {
      setVersions(await listKeyVersions(key.id));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">KMS</p>
          <h1>Keys</h1>
        </div>
        <button type="button" onClick={loadKeys}>
          Refresh
        </button>
      </header>

      {error ? <p className="error-message">{error}</p> : null}
      {message ? <p className="success-message">{message}</p> : null}

      {canManage ? (
        <form className="form-panel" onSubmit={handleCreateKey}>
          <h2>Create Key</h2>
          <div className="form-grid">
            <label>
              Name
              <input
                value={form.name}
                onChange={(event) => updateForm("name", event.target.value)}
                required
                minLength="3"
              />
            </label>
            <label>
              Algorithm
              <input value={form.algorithm} readOnly />
            </label>
          </div>
          <label>
            Description
            <input
              value={form.description}
              onChange={(event) => updateForm("description", event.target.value)}
            />
          </label>
          <button type="submit">Create key</button>
        </form>
      ) : null}

      {selectedKey ? (
        <section className="panel">
          <h2>Versions for {selectedKey.name}</h2>
          <div className="version-list">
            {versions.map((version) => (
              <div className="version-item" key={version.id}>
                <strong>v{version.version_number}</strong>
                <span>{version.is_active ? "active" : "old"}</span>
                <span>{formatDate(version.created_at)}</span>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {isLoading ? <p className="muted-text">Loading keys</p> : null}
      <DataTable columns={columns} rows={keys} />
    </section>
  );
}
