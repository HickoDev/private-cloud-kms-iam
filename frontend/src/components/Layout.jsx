const navItems = [
  { href: "#/", label: "Dashboard" },
  { href: "#/login", label: "Login" },
  { href: "#/users", label: "Users" },
  { href: "#/keys", label: "Keys" },
  { href: "#/crypto", label: "Crypto" },
  { href: "#/audit-logs", label: "Audit Logs" },
];

export default function Layout({ children, currentPath }) {
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
          {navItems.map((item) => {
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
      </aside>

      <main className="content">{children}</main>
    </div>
  );
}

