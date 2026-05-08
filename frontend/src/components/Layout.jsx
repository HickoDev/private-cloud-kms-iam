const navItems = [
  { href: "#/", label: "Dashboard", roles: [] },
  { href: "#/users", label: "Users", roles: ["ADMIN"] },
  { href: "#/keys", label: "Keys", roles: ["ADMIN", "KEY_MANAGER", "KEY_USER", "AUDITOR"] },
  { href: "#/crypto", label: "Crypto", roles: ["ADMIN", "KEY_USER"] },
  { href: "#/audit-logs", label: "Audit Logs", roles: ["ADMIN", "AUDITOR"] },
];

function canViewItem(user, item) {
  if (!user) {
    return item.href === "#/login";
  }

  return item.roles.length === 0 || item.roles.some((role) => user.roles.includes(role));
}

export default function Layout({ children, currentPath, user, onLogout }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">KMS</span>
          <div>
            <strong>Mini IAM</strong>
            <span>Private Cloud</span>
          </div>
        </div>

        <nav className="nav-list" aria-label="Main navigation">
          {navItems.filter((item) => canViewItem(user, item)).map((item) => {
            const itemPath = item.href.replace("#", "");
            const isActive = currentPath === itemPath;

            return (
              <a
                key={item.href}
                className={isActive ? "nav-link active" : "nav-link"}
                href={item.href}
              >
                {item.label}
              </a>
            );
          })}
        </nav>

        {user ? (
          <div className="user-panel">
            <strong>{user.email}</strong>
            <span>{user.roles.join(", ")}</span>
            <button type="button" className="secondary-button" onClick={onLogout}>
              Logout
            </button>
          </div>
        ) : null}
      </aside>

      <main className="content">{children}</main>
    </div>
  );
}
