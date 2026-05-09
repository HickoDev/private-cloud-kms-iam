import { useEffect, useMemo, useState } from "react";

import DataTable from "../components/DataTable.jsx";
import {
  createKey,
  disableKey,
  grantKeyAccess,
  listKeyVersions,
  listKeyAccess,
  listKeys,
  revokeKeyAccess,
  rotateKey,
} from "../services/keyService.js";
import { listUsers } from "../services/userService.js";

function canManageKeys(user) {
  return user?.permissions?.includes("KEY_CREATE");
}

function canManageKeyAccess(user) {
  return user?.permissions?.includes("KEY_ACCESS_MANAGE");
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString() : "-";
}

export default function KeysPage({ user }) {
  const [keys, setKeys] = useState([]);
  const [versions, setVersions] = useState([]);
  const [selectedKey, setSelectedKey] = useState(null);
  const [accessKey, setAccessKey] = useState(null);
  const [accessList, setAccessList] = useState([]);
  const [users, setUsers] = useState([]);
  const [accessForm, setAccessForm] = useState({
    userId: "",
    canEncrypt: true,
    canDecrypt: true,
  });
  const [form, setForm] = useState({
    name: "",
    description: "",
    algorithm: "AES-256-GCM",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const canManage = canManageKeys(user);
  const canAssignAccess = canManageKeyAccess(user);

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
            {canAssignAccess ? (
              <button
                type="button"
                className="secondary-button compact-button"
                onClick={() => loadAccess(row)}
              >
                Access
              </button>
            ) : null}
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
    [canAssignAccess, canManage],
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

  async function loadAccess(key) {
    setError("");
    setAccessKey(key);

    try {
      const [accessData, usersData] = await Promise.all([listKeyAccess(key.id), listUsers()]);
      setAccessList(accessData);
      setUsers(usersData.filter((item) => item.is_active));
      const firstUser = usersData.find((item) => item.is_active);
      setAccessForm({
        userId: firstUser ? String(firstUser.id) : "",
        canEncrypt: true,
        canDecrypt: true,
      });
    } catch (err) {
      setError(err.message);
    }
  }

  function updateAccessForm(field, value) {
    setAccessForm((current) => ({ ...current, [field]: value }));
  }

  async function handleGrantAccess(event) {
    event.preventDefault();
    if (!accessKey) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await grantKeyAccess(accessKey.id, {
        user_id: Number(accessForm.userId),
        can_encrypt: accessForm.canEncrypt,
        can_decrypt: accessForm.canDecrypt,
      });
      setMessage("Key access updated.");
      await loadAccess(accessKey);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRevokeAccess(entry) {
    if (!accessKey) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await revokeKeyAccess(accessKey.id, entry.user_id);
      setMessage("Key access revoked.");
      await loadAccess(accessKey);
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

      {accessKey ? (
        <section className="form-panel">
          <h2>Access for {accessKey.name}</h2>
          <form className="nested-form" onSubmit={handleGrantAccess}>
            <div className="form-grid">
              <label>
                User
                <select
                  value={accessForm.userId}
                  onChange={(event) => updateAccessForm("userId", event.target.value)}
                  required
                >
                  {users.length === 0 ? <option value="">No active users</option> : null}
                  {users.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.email}
                    </option>
                  ))}
                </select>
              </label>
              <label className="checkbox-label align-end">
                <input
                  type="checkbox"
                  checked={accessForm.canEncrypt}
                  onChange={(event) => updateAccessForm("canEncrypt", event.target.checked)}
                />
                Can encrypt
              </label>
              <label className="checkbox-label align-end">
                <input
                  type="checkbox"
                  checked={accessForm.canDecrypt}
                  onChange={(event) => updateAccessForm("canDecrypt", event.target.checked)}
                />
                Can decrypt
              </label>
            </div>
            <div className="button-row">
              <button type="submit" disabled={!accessForm.userId}>
                Grant access
              </button>
              <button
                type="button"
                className="secondary-button compact-button"
                onClick={() => setAccessKey(null)}
              >
                Close
              </button>
            </div>
          </form>

          <div className="access-list">
            {accessList.length === 0 ? (
              <p className="muted-text">No users assigned to this key.</p>
            ) : (
              accessList.map((entry) => (
                <div className="access-item" key={entry.id}>
                  <div>
                    <strong>{entry.email}</strong>
                    <span>
                      encrypt={String(entry.can_encrypt)}, decrypt={String(entry.can_decrypt)}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="danger-button compact-button"
                    onClick={() => handleRevokeAccess(entry)}
                  >
                    Revoke
                  </button>
                </div>
              ))
            )}
          </div>
        </section>
      ) : null}

      {isLoading ? <p className="muted-text">Loading keys</p> : null}
      <DataTable columns={columns} rows={keys} />
    </section>
  );
}
