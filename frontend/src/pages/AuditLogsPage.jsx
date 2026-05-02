import DataTable from "../components/DataTable.jsx";

const columns = [
  { key: "createdAt", label: "Time" },
  { key: "action", label: "Action" },
  { key: "status", label: "Status" },
  { key: "details", label: "Details" },
];

export default function AuditLogsPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Traceability</p>
          <h1>Audit Logs</h1>
        </div>
      </header>

      <DataTable columns={columns} rows={[]} />
    </section>
  );
}

