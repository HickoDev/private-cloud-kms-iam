const stats = [
  { label: "Users", value: "0" },
  { label: "Keys", value: "0" },
  { label: "Active keys", value: "0" },
  { label: "Audit logs", value: "0" },
];

export default function DashboardPage({ user }) {
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
