import { useEffect, useState } from "react";

import { listAuditLogs } from "../services/auditService.js";
import { listKeys } from "../services/keyService.js";
import { listUsers } from "../services/userService.js";

export default function DashboardPage({ user }) {
  const [stats, setStats] = useState([
    { label: "Users", value: "-" },
    { label: "Keys", value: "-" },
    { label: "Active keys", value: "-" },
    { label: "Audit logs", value: "-" },
  ]);

  useEffect(() => {
    async function loadStats() {
      const [usersResult, keysResult, auditResult] = await Promise.allSettled([
        user?.permissions?.includes("USER_READ") ? listUsers() : Promise.resolve(null),
        user?.permissions?.includes("KEY_READ") ? listKeys() : Promise.resolve(null),
        user?.permissions?.includes("AUDIT_READ") ? listAuditLogs() : Promise.resolve(null),
      ]);

      const users = usersResult.status === "fulfilled" ? usersResult.value : null;
      const keys = keysResult.status === "fulfilled" ? keysResult.value : null;
      const auditLogs = auditResult.status === "fulfilled" ? auditResult.value : null;

      setStats([
        { label: "Users", value: users ? String(users.length) : "N/A" },
        { label: "Keys", value: keys ? String(keys.length) : "N/A" },
        {
          label: "Active keys",
          value: keys ? String(keys.filter((key) => key.status === "ACTIVE").length) : "N/A",
        },
        { label: "Audit logs", value: auditLogs ? String(auditLogs.length) : "N/A" },
      ]);
    }

    loadStats();
  }, [user]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h1>Security Dashboard</h1>
        </div>
        <span className="status-pill">{user?.roles?.[0] || "Authenticated"}</span>
      </header>

      <div className="stats-grid">
        {stats.map((stat) => (
          <article className="stat-card" key={stat.label}>
            <span>{stat.label}</span>
            <strong>{stat.value}</strong>
          </article>
        ))}
      </div>

      <section className="panel">
        <h2>Session</h2>
        <p>{user?.email}</p>
      </section>
    </section>
  );
}
