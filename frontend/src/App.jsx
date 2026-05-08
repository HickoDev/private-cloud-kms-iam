import { useEffect, useMemo, useState } from "react";

import Layout from "./components/Layout.jsx";
import AuditLogsPage from "./pages/AuditLogsPage.jsx";
import CryptoPage from "./pages/CryptoPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import KeysPage from "./pages/KeysPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import UsersPage from "./pages/UsersPage.jsx";
import { getStoredToken } from "./services/api.js";
import { getCurrentUser, logout as logoutUser } from "./services/authService.js";

const routes = {
  "/": { Page: DashboardPage, roles: [] },
  "/login": { Page: LoginPage, roles: [] },
  "/users": { Page: UsersPage, roles: ["ADMIN"] },
  "/keys": { Page: KeysPage, roles: ["ADMIN", "KEY_MANAGER", "KEY_USER", "AUDITOR"] },
  "/crypto": { Page: CryptoPage, roles: ["ADMIN", "KEY_USER"] },
  "/audit-logs": { Page: AuditLogsPage, roles: ["ADMIN", "AUDITOR"] },
};

function getCurrentPath() {
  return window.location.hash.replace("#", "") || "/";
}

export default function App() {
  const [path, setPath] = useState(getCurrentPath);
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const handleHashChange = () => setPath(getCurrentPath());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    async function loadUser() {
      if (!getStoredToken()) {
        setAuthChecked(true);
        if (getCurrentPath() !== "/login") {
          window.location.hash = "/login";
        }
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        logoutUser();
        setUser(null);
        window.location.hash = "/login";
      } finally {
        setAuthChecked(true);
      }
    }

    loadUser();
  }, []);

  const activeRoute = useMemo(() => routes[path] || routes["/"], [path]);
  const Page = activeRoute.Page;
  const isLoginPage = path === "/login";
  const canAccess =
    isLoginPage ||
    activeRoute.roles.length === 0 ||
    activeRoute.roles.some((role) => user?.roles?.includes(role));

  function handleLogin(nextUser) {
    setUser(nextUser);
    window.location.hash = "/";
  }

  function handleLogout() {
    logoutUser();
    setUser(null);
    window.location.hash = "/login";
  }

  if (!authChecked) {
    return <div className="boot-screen">Loading</div>;
  }

  if (!user && !isLoginPage) {
    return null;
  }

  return (
    <Layout currentPath={path} user={user} onLogout={handleLogout}>
      {canAccess ? (
        <Page user={user} onLogin={handleLogin} />
      ) : (
        <section className="page">
          <header className="page-header">
            <div>
              <p className="eyebrow">Access</p>
              <h1>Denied</h1>
            </div>
          </header>
        </section>
      )}
    </Layout>
  );
}
