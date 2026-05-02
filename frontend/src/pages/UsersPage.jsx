import DataTable from "../components/DataTable.jsx";

const columns = [
  { key: "email", label: "Email" },
  { key: "roles", label: "Roles" },
  { key: "status", label: "Status" },
];

export default function UsersPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Mini-IAM</p>
          <h1>Users</h1>
        </div>
        <button type="button">Create user</button>
      </header>

      <DataTable columns={columns} rows={[]} />
    </section>
  );
}

