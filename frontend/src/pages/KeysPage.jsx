import DataTable from "../components/DataTable.jsx";

const columns = [
  { key: "name", label: "Name" },
  { key: "algorithm", label: "Algorithm" },
  { key: "status", label: "Status" },
  { key: "activeVersion", label: "Active Version" },
];

export default function KeysPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">KMS</p>
          <h1>Keys</h1>
        </div>
        <button type="button">Create key</button>
      </header>

      <DataTable columns={columns} rows={[]} />
    </section>
  );
}

