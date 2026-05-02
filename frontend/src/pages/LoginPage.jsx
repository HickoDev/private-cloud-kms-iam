export default function LoginPage() {
  return (
    <section className="page narrow-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Authentication</p>
          <h1>Login</h1>
        </div>
      </header>

      <form className="form-panel">
        <label>
          Email
          <input type="email" placeholder="admin@example.com" />
        </label>
        <label>
          Password
          <input type="password" placeholder="admin123" />
        </label>
        <button type="button">Sign in</button>
      </form>
    </section>
  );
}

