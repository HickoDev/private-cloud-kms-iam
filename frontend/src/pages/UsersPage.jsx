import { useEffect, useMemo, useState } from "react";

import DataTable from "../components/DataTable.jsx";
import {
  assignRoles,
  createUser,
  listRoles,
  listUsers,
  updateUser,
} from "../services/userService.js";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedRoles, setSelectedRoles] = useState([]);
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    roles: ["KEY_USER"],
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const columns = useMemo(
    () => [
      { key: "email", label: "Email" },
      { key: "username", label: "Username" },
      {
        key: "roles",
        label: "Roles",
        render: (row) => row.roles.join(", ") || "None",
      },
      {
        key: "status",
        label: "Status",
        render: (row) => (row.is_active ? "Active" : "Inactive"),
      },
      {
        key: "actions",
        label: "Actions",
        render: (row) => (
          <div className="table-actions">
            <button type="button" onClick={() => startRoleEdit(row)}>
              Roles
            </button>
            <button
              type="button"
              className="secondary-button compact-button"
              onClick={() => toggleUserStatus(row)}
            >
              {row.is_active ? "Deactivate" : "Activate"}
            </button>
          </div>
        ),
      },
    ],
    [roles],
  );

  async function loadData() {
    setError("");
    setIsLoading(true);

    try {
      const [usersData, rolesData] = await Promise.all([listUsers(), listRoles()]);
      setUsers(usersData);
      setRoles(rolesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function updateForm(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function toggleFormRole(roleName) {
    setForm((current) => {
      const hasRole = current.roles.includes(roleName);
      return {
        ...current,
        roles: hasRole
          ? current.roles.filter((role) => role !== roleName)
          : [...current.roles, roleName],
      };
    });
  }

  function toggleSelectedRole(roleName) {
    setSelectedRoles((current) =>
      current.includes(roleName)
        ? current.filter((role) => role !== roleName)
        : [...current, roleName],
    );
  }

  async function handleCreateUser(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      await createUser(form);
      setForm({ username: "", email: "", password: "", roles: ["KEY_USER"] });
      setMessage("User created.");
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  function startRoleEdit(user) {
    setSelectedUser(user);
    setSelectedRoles(user.roles);
    setMessage("");
    setError("");
  }

  async function saveRoles() {
    if (!selectedUser) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await assignRoles(selectedUser.id, selectedRoles);
      setSelectedUser(null);
      setSelectedRoles([]);
      setMessage("Roles updated.");
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function toggleUserStatus(user) {
    setError("");
    setMessage("");

    try {
      await updateUser(user.id, { is_active: !user.is_active });
      setMessage("User status updated.");
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Mini-IAM</p>
          <h1>Users</h1>
        </div>
        <button type="button" onClick={loadData}>
          Refresh
        </button>
      </header>

      {error ? <p className="error-message">{error}</p> : null}
      {message ? <p className="success-message">{message}</p> : null}

      <form className="form-panel" onSubmit={handleCreateUser}>
        <h2>Create User</h2>
        <div className="form-grid">
          <label>
            Username
            <input
              value={form.username}
              onChange={(event) => updateForm("username", event.target.value)}
              required
              minLength="3"
            />
          </label>
          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(event) => updateForm("email", event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={(event) => updateForm("password", event.target.value)}
              required
              minLength="6"
            />
          </label>
        </div>
        <div className="checkbox-row">
          {roles.map((role) => (
            <label key={role.id} className="checkbox-label">
              <input
                type="checkbox"
                checked={form.roles.includes(role.name)}
                onChange={() => toggleFormRole(role.name)}
              />
              {role.name}
            </label>
          ))}
        </div>
        <button type="submit">Create user</button>
      </form>

      {selectedUser ? (
        <section className="form-panel">
          <h2>Assign Roles</h2>
          <p className="muted-text">{selectedUser.email}</p>
          <div className="checkbox-row">
            {roles.map((role) => (
              <label key={role.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selectedRoles.includes(role.name)}
                  onChange={() => toggleSelectedRole(role.name)}
                />
                {role.name}
              </label>
            ))}
          </div>
          <div className="button-row">
            <button type="button" onClick={saveRoles}>
              Save roles
            </button>
            <button
              type="button"
              className="secondary-button compact-button"
              onClick={() => setSelectedUser(null)}
            >
              Cancel
            </button>
          </div>
        </section>
      ) : null}

      {isLoading ? <p className="muted-text">Loading users</p> : null}
      <DataTable columns={columns} rows={users} />
    </section>
  );
}
