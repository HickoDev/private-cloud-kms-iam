const stats = [
  { label: "Users", value: "0" },
  { label: "Keys", value: "0" },
  { label: "Active keys", value: "0" },
  { label: "Audit logs", value: "0" },
];

export default function DashboardPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h1>Security Dashboard</h1>
        </div>
        <span className="status-pill">Skeleton ready</span>
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
        <h2>Current Build Step</h2>
        <p>
          The interface is wired as a dashboard shell. Real data will be added
          after backend authentication, RBAC, KMS, and audit modules are
          implemented.
        </p>
      </section>
    </section>
  );
}

