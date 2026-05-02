export default function CryptoPage() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">KMS Operation</p>
          <h1>Encrypt / Decrypt</h1>
        </div>
      </header>

      <div className="split-grid">
        <form className="form-panel">
          <h2>Encrypt</h2>
          <label>
            Key
            <select>
              <option>No keys yet</option>
            </select>
          </label>
          <label>
            Plaintext
            <textarea rows="8" />
          </label>
          <button type="button">Encrypt</button>
        </form>

        <form className="form-panel">
          <h2>Decrypt</h2>
          <label>
            Ciphertext
            <textarea rows="8" />
          </label>
          <label>
            Nonce
            <input type="text" />
          </label>
          <button type="button">Decrypt</button>
        </form>
      </div>
    </section>
  );
}

