import { useEffect, useMemo, useState } from "react";

import Layout from "./components/Layout.jsx";
import AuditLogsPage from "./pages/AuditLogsPage.jsx";
import CryptoPage from "./pages/CryptoPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import KeysPage from "./pages/KeysPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import UsersPage from "./pages/UsersPage.jsx";

const routes = {
  "/": DashboardPage,
  "/login": LoginPage,
  "/users": UsersPage,
  "/keys": KeysPage,
  "/crypto": CryptoPage,
  "/audit-logs": AuditLogsPage,
};

function getCurrentPath() {
  return window.location.hash.replace("#", "") || "/";
}

export default function App() {
  const [path, setPath] = useState(getCurrentPath);

  useEffect(() => {
    const handleHashChange = () => setPath(getCurrentPath());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const Page = useMemo(() => routes[path] || DashboardPage, [path]);

  return (
    <Layout currentPath={path}>
      <Page />
    </Layout>
  );
}

